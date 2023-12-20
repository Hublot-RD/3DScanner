import os
import cv2
import numpy as np
import pyexiv2

def create_circular_kernel(size):
    radius = size[0] // 2
    y, x = np.ogrid[:size[0], :size[1]]
    circular_kernel = (x - radius)**2 + (y - radius)**2 <= radius**2
    return circular_kernel.astype(np.uint8)

def show_image(image, title="Image"):
    cv2.imshow(title, cv2.resize(image, (1000, 600)))

def blue_shift(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_b = np.average(result[:, :, 2])
    if avg_b - 128 >= -8: # Image is too yellow
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128 + 8) * (result[:, :, 0] / 255.0))
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result
    else:
        return img

def create_mask_from_hue(image_path, crop_img=False, debug=False) -> np.ndarray:
    # Load the image
    img_original = cv2.imread(image_path)
    if debug: show_image(img_original, "Original")

    # Perform white balance
    img = blue_shift(img_original)
    if debug: show_image(img, "Blue shifted")

    # Convert the image to hue only
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img = img[:, :, 0]
    if debug: show_image(img, "Hue")

    # Normalise image
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    if debug: show_image(img, "Hue normalized")

    # Threshold
    _, hot_colors = cv2.threshold(img, thresh=90, maxval=255, type=cv2.THRESH_BINARY_INV)
    _, cold_colors = cv2.threshold(img, thresh=120, maxval=255, type=cv2.THRESH_BINARY_INV)
    # if debug: show_image(hot_colors, "Hot colors")
    # if debug: show_image(cold_colors, "Cold colors")
    mask = cv2.bitwise_and(hot_colors, cold_colors)
    if debug: show_image(mask, "After thresholding")
    kernel_size = (255, 255)
    blured_mask = cv2.GaussianBlur(mask, kernel_size, 0)
    if debug: show_image(blured_mask, "After thresholding and bluring")
    _, mask = cv2.threshold(blured_mask, thresh=10, maxval=255, type=cv2.THRESH_BINARY)
    if debug: show_image(mask, "After another thresholding")

    # Keep only biggest region
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [max_contour], 0, 255, -1)
        if debug: show_image(mask, "Contour mask")
    else:
        print("No contours found")

    # Add margin to mask
    kernel = create_circular_kernel((127, 127))
    mask = cv2.dilate(mask, kernel, iterations=1)
    if debug: show_image(mask, "After dilating")

    # Fill shape and crop
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [max_contour], 0, 255, -1)
        if debug: show_image(mask, "Contour mask")

        if crop_img:
            # Find bounding rectangle
            [x, y, w, h] = cv2.boundingRect(max_contour)

            boundaries.append([x, y, w, h])

            # Crop image and mask to bounding rectangle
            img_original = img_original[y:y+h, x:x+w]
            mask = mask[y:y+h, x:x+w]
            if debug: show_image(img_original, "Cropped image")
    else:
        print("No contours found")

    # Reshape mask to three channels
    mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)

    return mask, img_original

# Usage
SOURCE_PATH = "C:/Users/v.philippoz/Documents/scanner3D/"
OBJECT_NAME = "etau_1812"
IMAGE_COUNT = 180
files = []
for i in range(IMAGE_COUNT):
    path = f"{SOURCE_PATH}{OBJECT_NAME}/{OBJECT_NAME}_" + "{:03d}.jpg".format(i+1)
    files.append(path)

boundaries = []

# Create output directory
if not os.path.exists(f"{SOURCE_PATH}{OBJECT_NAME}/msk/"):
    os.makedirs(f"{SOURCE_PATH}{OBJECT_NAME}/msk/")


merged = cv2.imread(files[0])
for i, in_path in enumerate(files):
    print(f"Processing image {i+1}/{len(files)}")
    # Load the image
    tmp_img = cv2.imread(in_path)
    # cv2.imshow("Before "+str(i+1), cv2.resize(tmp_img, (1000, 600)))
    
    # Merge the image to get a better idea of the object boundary
    merged = cv2.addWeighted(merged, i/(i+1), tmp_img, 1/(i+1), 0)

    # # Create the mask
    # mask, img = create_mask_from_hue(in_path, crop_img=True, debug=False)

    # # Save the mask
    # out_path = f"{SOURCE_PATH}{OBJECT_NAME}/msk/{OBJECT_NAME}_" + "{:03d}_msk.jpg".format(i+1)
    # cv2.imwrite(out_path, mask)

    # # Save the cropped image
    # out_path = f"{SOURCE_PATH}{OBJECT_NAME}/cropped/{OBJECT_NAME}_" + "{:03d}.jpg".format(i+1)
    # cv2.imwrite(out_path, img)

    # # Copy metadata from original image to cropped image
    # in_metadata = pyexiv2.Image(in_path)
    # out_metadata = pyexiv2.Image(out_path)
    # out_metadata.modify_exif(in_metadata.read_exif())

# print("Boundaries:", boundaries)

out_path = f"{SOURCE_PATH}{OBJECT_NAME}/{OBJECT_NAME}_merged.jpg"
cv2.imwrite(out_path, merged)


cv2.waitKey(0)
cv2.destroyAllWindows()