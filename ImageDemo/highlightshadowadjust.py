import cv2
import numpy as np

def high_light_shadow_adjust_lab(image, highlight_threshold=180, shadow_threshold=50, highlight_factor=1.1, shadow_factor=1.2):
    """
    Enhance highlights and shadows in an image using CLAHE, and adjust brightness in L*a*b* color space to avoid color shifts.
    
    :param image: Input image (BGR)
    :param highlight_threshold: Threshold for highlights detection
    :param shadow_threshold: Threshold for shadows detection
    :param highlight_factor: Enhancement factor for highlights (with limits to prevent overexposure)
    :param shadow_factor: Enhancement factor for shadows
    :return: Image with enhanced highlights and shadows with smoother transition
    """
    # Convert image to L*a*b* color space
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

    # Split L*a*b* into L (luminance), a, and b channels
    L, a, b = cv2.split(lab_image)

    # Create masks for highlights and shadows based on thresholds in L channel (luminance)
    highlight_mask = L > highlight_threshold  # High brightness regions
    shadow_mask = L < shadow_threshold  # Low brightness regions

    # Apply CLAHE to L channel (luminance)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    L_clahe = clahe.apply(L)

    # Enhance highlights by gently increasing luminance (L channel)
    L_clahe[highlight_mask] = np.clip(L_clahe[highlight_mask] * highlight_factor, 0, 255)

    # Enhance shadows by increasing luminance (L channel)
    # Directly apply the shadow enhancement by scaling the luminance values
    L_clahe[shadow_mask] = np.clip(L_clahe[shadow_mask] * shadow_factor + 50, 0, 255)

    # Merge the modified L channel back with the original a and b channels
    lab_enhanced = cv2.merge([L_clahe, a, b])

    # Convert the enhanced L*a*b* image back to BGR
    enhanced_image = cv2.cvtColor(lab_enhanced, cv2.COLOR_Lab2BGR)

    # Apply Gaussian blur to smooth out harsh transitions between enhanced and non-enhanced areas
    final_image = cv2.GaussianBlur(enhanced_image, (7, 7), 0)

    return final_image

# Read the image (input.webp)
image = cv2.imread('input.webp')

# Check if the image was successfully loaded
if image is None:
    print("Error: Unable to load the image.")
else:
    # Apply highlight and shadow adjustment with LAB color space
    adjusted_image = high_light_shadow_adjust_lab(image, highlight_factor=1.0, shadow_factor=0.4)
    
    cv2.imwrite('./hsa_python.png', adjusted_image)
    # # Display the original and adjusted images
    # cv2.imshow('Original Image', image)
    # cv2.imshow('Adjusted Image with LAB', adjusted_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()