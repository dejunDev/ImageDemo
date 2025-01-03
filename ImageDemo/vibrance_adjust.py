import cv2
import numpy as np


def vibrance_adjust(image, vibrance=1.5):
    # 将图像转换为浮动范围 [0, 1]
    image = image.astype(np.float32) / 255.0

    # 提取 RGB 通道
    r, g, b = cv2.split(image)

    # 计算亮度（加权 RGB）
    brightness = 0.393 * r + 0.769 * g + 0.189 * b

    # 计算 RGB 的最大值和最小值
    max_val = np.maximum(r, np.maximum(g, b))
    min_val = np.minimum(r, np.minimum(g, b))

    # 计算鲜艳度调整比例
    adjustment = 1.0 - max_val
    adjustment = adjustment + min_val
    adjustment = adjustment * vibrance
    adjustment = adjustment + 1.0

    # 应用鲜艳度调整
    r = r * adjustment
    g = g * adjustment
    b = b * adjustment

    # 限制每个通道的值范围 [0, 1]
    r = np.clip(r, 0.0, 1.0)
    g = np.clip(g, 0.0, 1.0)
    b = np.clip(b, 0.0, 1.0)

    # 合并回 RGB 图像
    output_image = cv2.merge([r, g, b])

    # 转换回 [0, 255] 范围并返回结果
    output_image = (output_image * 255).astype(np.uint8)
    return output_image


# 加载图像
image = cv2.imread('input_image.jpg')

# 调整鲜艳度
vibrant_image = vibrance_adjust(image, vibrance=1.5)

# 显示原始图像和调整后的图像
cv2.imshow("Original Image", image)
cv2.imshow("Vibrant Image", vibrant_image)

cv2.waitKey(0)
cv2.destroyAllWindows()