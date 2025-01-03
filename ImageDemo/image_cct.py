import cv2
import numpy as np
from sklearn.cluster import KMeans


# RGB 转 XYZ 的转换矩阵（基于 sRGB 色彩空间）
def rgb_to_xyz(r, g, b):
    # 归一化 RGB 值
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    # 线性化 RGB
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # 转换到 XYZ 颜色空间
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    return x, y, z


# 根据 XYZ 估算色温（使用 McCamy 公式）
def xyz_to_color_temperature(x, y, z):
    # 归一化色度坐标
    xn = x / (x + y + z)
    yn = y / (x + y + z)

    # McCamy's 色温估算公式
    n = (xn - 0.3320) / (0.1858 - yn)
    cct = 437 * (n ** 3) + 3601 * (n ** 2) + 6861 * n + 5517

    return cct


# 主函数：RGB -> 色温
def rgb_to_color_temperature(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    cct = xyz_to_color_temperature(x, y, z)
    return cct


def rgb_to_kelvin(r, g, b):
    # 归一化 RGB 值到 0-1 范围
    r_normalized = r / 255.0
    g_normalized = g / 255.0
    b_normalized = b / 255.0

    # 使用 RGB 通道的加权和进行色温估算
    # 通过拟合 RGB 到色温的关系
    X = r_normalized * 0.257 + g_normalized * 0.434 + b_normalized * 0.091
    Y = r_normalized * 0.247 + g_normalized * 0.420 + b_normalized * 0.065

    # 计算色温的近似值，使用黑体辐射的经验公式
    if X + Y > 0.01:
        kelvin = 10000 / ((X + Y) ** 0.5)
    else:
        kelvin = 6500  # 默认色温为6500K，表示标准日光

    # 返回估算的色温
    return int(kelvin) - 6500


def calculate_average_color(img):
    # 转换为 RGB 模式（如果是其他模式，比如 RGBA、灰度等，先转换为 RGB）
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 将图像数据转换为 numpy 数组
    img_data = np.array(img)

    # 计算每个通道的平均值（R, G, B）
    avg_r = np.mean(img_data[:, :, 0])
    avg_g = np.mean(img_data[:, :, 1])
    avg_b = np.mean(img_data[:, :, 2])

    # 返回平均颜色值
    return avg_r, avg_g, avg_b


def kmeans_weighted_average_color(img, k=3):
    # 转换为 RGB 模式
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 将图像转换为 numpy 数组并展平为二维数组 (每个像素是一个点)
    img_data = np.array(img)
    pixels = img_data.reshape((-1, 3))  # 每行是一个RGB像素

    # 使用 KMeans 聚类
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)

    # 获取聚类中心（每个类的平均颜色）
    centers = kmeans.cluster_centers_

    # 获取每个聚类的样本数量（权重）
    labels = kmeans.labels_
    unique_labels, label_counts = np.unique(labels, return_counts=True)

    # 计算加权平均
    weighted_sum = np.zeros(3)
    total_weight = 0

    for i, label in enumerate(unique_labels):
        cluster_center = centers[label]
        weight = label_counts[i]
        weighted_sum += cluster_center * weight
        total_weight += weight

    # 计算加权平均颜色
    weighted_average = weighted_sum / total_weight

    # 返回加权平均的 RGB 值
    return tuple(np.round(weighted_average).astype(int))


def extract_highlight_excluding_multiple(img, threshold=200, white_threshold=254, dark_threshold=20):
    # 将图像转换为 RGB（如果是 BGR 格式）
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 将图像转换为 numpy 数组
    img_data = np.array(img)

    # 计算每个像素的亮度
    luminance = 0.2989 * img_data[:, :, 0] + 0.5870 * img_data[:, :, 1] + 0.1140 * img_data[:, :, 2]

    # 找出亮度高于阈值的高光部分，但排除以下条件的像素：
    # 1. 纯白色或接近白色像素（R, G, B 大于 white_threshold）
    # 2. 极暗像素（亮度低于 dark_threshold）
    highlights = img_data[
        (luminance >= threshold) &
        ~np.all(img_data >= white_threshold, axis=-1) &  # 排除近白色
        (luminance > dark_threshold)  # 排除极暗像素
        ]

    # 如果没有高光部分，返回一个提示
    if highlights.size == 0:
        return None

    # 计算高光部分的平均颜色
    avg_highlight_color = np.mean(highlights, axis=0)

    return tuple(np.round(avg_highlight_color).astype(int))


def calculate_tint_hsl(r, g, b):
    max_value = 1e6  # 设置一个最大值阈值
    r = np.clip(r, -max_value, max_value)
    b = np.clip(b, -max_value, max_value)
    return (r - b) / (r + b) if (r + b) != 0 else 0


# 6110
image_path = "img_0.png"  # 替换为你的图片路径
image = cv2.imread(image_path)


def find_max_white_point(img, threshold=240):
    """
    在图像中找到最大白点（忽略纯白），并返回该像素的 RGB 值。
    :param img: 输入图像（BGR格式）
    :param threshold: 亮度的阈值，默认为240，用来排除亮度过低的白色像素。
    :return: 最大白点的 RGB 值
    """
    # 将图像转换为 RGB 格式
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 计算每个像素的亮度（采用加权法）
    luminance = 0.2989 * img_rgb[:, :, 0] + 0.5870 * img_rgb[:, :, 1] + 0.1140 * img_rgb[:, :, 2]

    # 找到亮度值高于阈值且不等于纯白（255, 255, 255）的像素
    mask = (luminance >= threshold) & ~np.all(img_rgb == [255, 255, 255], axis=-1)

    # 从符合条件的像素中找到最大亮度的点
    if np.any(mask):
        max_luminance_pixel = img_rgb[mask]
        max_pixel = max_luminance_pixel[np.argmax(np.sum(max_luminance_pixel, axis=1))]  # 最大亮度的像素
        return tuple(max_pixel)
    else:
        return None  # 如果没有符合条件的像素


def find_brightest_point(image):
    # 将图像从 BGR 转换为 RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 计算每个像素的亮度，选择 RGB 中的最大值作为亮度值
    brightness = np.max(image_rgb, axis=2)

    # 找到亮度值最大的像素位置
    y, x = np.unravel_index(np.argmax(brightness), brightness.shape)

    # 获取最亮像素的 RGB 值
    brightest_pixel = image_rgb[y, x]

    return brightest_pixel


def color_based_white_balance(image, threshold=10):
    # 将图像从 BGR 转换为 RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 计算每个像素的亮度（加权 RGB 通道）
    luminance = 0.2126 * image_rgb[..., 0] + 0.7152 * image_rgb[..., 1] + 0.0722 * image_rgb[..., 2]

    # 假设最大亮度是 255（理想的白点）
    max_luminance = 255

    # 计算每个像素与最大亮度的差异
    luminance_diff = np.abs(luminance - max_luminance)

    # 找到亮度差异小于阈值的所有像素
    white_candidate_pixels = np.where(luminance_diff < threshold)

    # 如果没有找到符合条件的像素，可以返回原图
    if len(white_candidate_pixels[0]) == 0:
        return 255, 255, 255

    # 获取符合条件的像素的 (x, y) 和亮度差异
    candidates = list(zip(white_candidate_pixels[0], white_candidate_pixels[1], luminance_diff[white_candidate_pixels]))

    # 按照亮度差异排序，选择亮度差异最小的像素
    candidates.sort(key=lambda x: x[2])  # 根据亮度差异进行排序

    # 选择亮度差异最小的像素作为白点
    x, y, _ = candidates[0]

    # 获取该白点的 RGB 值
    return image_rgb[x, y]


def cie76_color_diff(c1, c2):
    """
    计算两个RGB颜色的CIE76色差。
    :param c1: 第一个颜色（RGB）
    :param c2: 第二个颜色（RGB）
    :return: 返回CIE76色差值
    """
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))


def find_neutral_point_rgb(image):
    """
    使用色差最小法在RGB颜色空间中找出中性点。
    :param image: 输入图像（BGR格式）。
    :return: 返回RGB值的中性点像素。
    """
    # 将图像从BGR转为RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 初始化变量
    neutral_pixel = None
    min_color_diff = float('inf')
    neutral_color = (255, 255, 255)  # 中性灰色

    # 遍历图像中的每个像素
    for y in range(image_rgb.shape[0]):
        for x in range(image_rgb.shape[1]):
            r, g, b = image_rgb[y, x]
            # 计算当前像素与中性灰色的CIE76色差
            color_diff = cie76_color_diff((r, g, b), neutral_color)

            # 找到最小色差的像素
            if color_diff < min_color_diff:
                min_color_diff = color_diff
                neutral_pixel = (r, g, b)

    # 返回找到的中性点RGB值
    return neutral_pixel


def find_neutral_point_max_contrast(image):
    """
    使用最大对比度法在Lab颜色空间中找出中性点。

    :param image: 输入图像（BGR格式）。
    :return: 返回RGB值的中性点像素。
    """
    # 将图像从BGR转换为Lab颜色空间
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

    # 提取Lab图像中的a和b通道
    a_channel = lab_image[:, :, 1]
    b_channel = lab_image[:, :, 2]

    # 计算每个像素的色度差（a和b通道的平方和）
    color_diff = np.sqrt(a_channel ** 2 + b_channel ** 2)

    # 找到色度差最小的像素
    min_color_diff_idx = np.unravel_index(np.argmin(color_diff), color_diff.shape)
    neutral_pixel_lab = lab_image[min_color_diff_idx]

    # 将该像素从Lab颜色空间转换回RGB
    neutral_pixel_rgb = cv2.cvtColor(np.uint8([[neutral_pixel_lab]]), cv2.COLOR_Lab2RGB)[0, 0]

    return tuple(neutral_pixel_rgb)


def find_neutral_point_histogram(image):
    """
    使用颜色直方图法找出中性点。

    :param image: 输入图像（BGR格式）。
    :return: 返回RGB值的中性点像素。
    """
    # 将图像从BGR转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 提取H通道（色调通道）
    h_channel = hsv_image[:, :, 0]

    # 计算H通道的直方图
    hist_h = cv2.calcHist([h_channel], [0], None, [256], [0, 256])

    # 找到色调值接近180的区域（灰色或白色通常在这个区域）
    neutral_hue_idx = np.argmin(np.abs(np.arange(256) - 180))

    # 根据最接近灰色的色调值找到相应的像素点
    neutral_pixels = np.where(h_channel == neutral_hue_idx)

    # 如果没有找到接近灰色的像素，返回图像的中心作为默认中性点
    if len(neutral_pixels[0]) == 0:
        neutral_pixel = (image.shape[1] // 2, image.shape[0] // 2)
        return tuple(image[neutral_pixel[1], neutral_pixel[0]])  # 返回RGB值

    # 找到最接近中性点的像素
    neutral_pixel = (neutral_pixels[1][0], neutral_pixels[0][0])
    return tuple(image[neutral_pixel[1], neutral_pixel[0]])


for i in range(10):
    image = cv2.imread(f"img_{i}.png")
    y = find_neutral_point_rgb(image)

    r = y[0]
    g = y[1]
    b = y[2]
    cct = rgb_to_color_temperature(r, g, b)
    tint = calculate_tint_hsl(r, g, b)
    print(f"img_{i}: r:{r} g:{g} b:{b}  估算的色温为: {cct:.2f} K  tint:{tint}")

# [6596.28 -0.80236]
