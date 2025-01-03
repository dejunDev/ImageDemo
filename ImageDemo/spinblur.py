import math

import cv2
import numpy as np


def apply_spin_blur(image, num_steps=30, delta_angle=0.0, blur_strength=5):
    # 获取图像的中心
    height, width = image.shape[:2]
    center = (width // 2, height // 2)

    # 输出图像
    output_image = np.zeros_like(image, dtype=np.float32)

    for step in range(num_steps):
        # 计算当前角度
        angle = step * delta_angle
        # 创建旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        # 旋转图像，确保输出图像尺寸足够大
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height), borderMode=cv2.BORDER_REFLECT)
        # 应用模糊
        blurred_image = cv2.GaussianBlur(rotated_image, (blur_strength, blur_strength), 0)
        # 将模糊图像叠加到输出图像
        output_image += blurred_image.astype(np.float32) / num_steps

    output_image = np.clip(output_image, 0, 255).astype(np.uint8)
    return output_image

#
# DazzCamera.SpinBlur 0x30148c5b0 - setDelta: 0.00025
# DazzCamera.SpinBlur 0x30148c5b0 - setInputImage: <CIImage: 0x303d91980 extent [0 0 2689 4033]>
# DazzCamera.SpinBlur 0x30148c5b0 - setNum: 30
# 读取图像
image = cv2.imread('3_DazzCamera.SpinBlur_setInputImage.png')
spin_blurred_image = apply_spin_blur(image, num_steps=30, delta_angle=0.0025 * (180 / math.pi), blur_strength=5)
cv2.imwrite('spin_blurred_image_raw.jpg', image)
cv2.imwrite('spin_blurred_image.jpg', spin_blurred_image)
