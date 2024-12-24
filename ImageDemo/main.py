import cv2
import numpy as np

# 读取图像
image = cv2.imread('input.webp')

# 应用高斯模糊
blurred_image = cv2.GaussianBlur(image,(7, 7),10)

cv2.imwrite('./gas_python.png', blurred_image)


