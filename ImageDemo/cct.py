import numpy as np
import scipy.optimize as optimize

# CIE 1931标准观察者颜色匹配函数矩阵
cie_matrix = np.array([[0.4124564, 0.3575761, 0.1804375],
                       [0.2126729, 0.7151522, 0.0721750],
                       [0.0193339, 0.1191920, 0.9503041]])

# 普朗克常数（单位：J·s）
h = 6.62607015e-34
# 真空中的光速（单位：m/s）
c = 299792458
# 玻尔兹曼常数（单位：J/K）
k = 1.380649e-23


# 将RGB转换为CIE 1931 XYZ颜色空间
def rgb_to_xyz(rgb):
    r, g, b = rgb / 255.0
    xyz = np.dot(cie_matrix, np.array([r, g, b]))
    return xyz


# 将CIE 1931 XYZ转换为CIE 1960 uv
def xyz_to_uv(xyz):
    x, y, z = xyz
    u = 4 * x / (x + 15 * y + 3 * z)
    v = 6 * y / (x + 15 * y + 3 * z)
    return np.array([u, v])


# 普朗克定律，计算黑体在给定波长和温度下的光谱辐射出射度
def planck_law(wavelength, temperature):
    return (2 * np.pi * h * c ** 2 / (wavelength ** 5)) * (1 / (np.exp((h * c) / (wavelength * k * temperature)) - 1))


# 根据CIE 1960 uv值计算色温（基于普朗克轨迹拟合）
def calculate_temperature_from_uv(uv):
    # 初始猜测温度范围
    initial_temperatures = np.linspace(4000, 10000, 10)
    min_error = float('inf')
    best_temperature = None
    for temp in initial_temperatures:
        wavelengths = np.array([380e-9, 450e-9, 550e-9, 650e-9, 780e-9])
        radiances = np.array([planck_law(wl, temp) for wl in wavelengths])
        xyz = np.dot(np.linalg.inv(cie_matrix), radiances)
        xyz /= np.sum(xyz)
        uv_calculated = xyz_to_uv(xyz)
        error = np.sum((uv - uv_calculated) ** 2)
        if error < min_error:
            min_error = error
            best_temperature = temp
    # 使用Nelder-Mead优化算法进一步优化温度值
    result = optimize.minimize(lambda t, uvv: np.sum((uvv - xyz_to_uv(np.dot(np.linalg.inv(cie_matrix),
                                                                             np.array([planck_law(wl, t) for wl in
                                                                                       wavelengths]))
                                                                      / np.sum(np.dot(np.linalg.inv(cie_matrix),
                                                                                      np.array(
                                                                                          [planck_law(wl, t) for wl in
                                                                                           wavelengths]))))) ** 2),
                               x0=best_temperature, args=(uv,), method='Nelder-Mead')
    return result.x[0]


# 计算RGB颜色的色温
def calculate_color_temperature(rgb):
    xyz = rgb_to_xyz(rgb)
    uv = xyz_to_uv(xyz)
    return calculate_temperature_from_uv(uv)


rgb = np.array([255, 255, 255])
print(calculate_color_temperature(rgb))
