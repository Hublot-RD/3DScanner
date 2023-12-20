# Crop a list of images to a given size
#
# Parameters:
#   images: list of images to crop
#   size: tuple (width, height) of the desired size
#   debug: if True, show debug images
#   show: if True, show the cropped images
#   save: if True, save the cropped images

import cv2 as cv
import os
import pyexiv2

def crop_images(images, size, debug=False, show=False, save=False):
    cropped_images = []
    for i,image in enumerate(images):
        print(f"Processing image {i+1}/{len(images)}")
        cropped_image = crop_image(image, size, debug, show, save)
        cropped_images.append(cropped_image)
    return cropped_images

def crop_image(image_path, size, debug=False, show=False, save=None):
    img = cv.imread(image_path)
    # Get image size
    height, width = img.shape[:2]
    # Compute crop size
    crop_height = min(height, size[0])
    crop_width = min(width, size[1])
    # Compute crop offset
    offset_x = (width - crop_width) // 2
    offset_y = (height - crop_height) // 2
    # Crop image
    cropped_image = img[offset_y:offset_y+crop_height, offset_x:offset_x+crop_width]
    # Show debug images
    if debug:
        cv.imshow("Original", cv.resize(img, (1000, 600)))
        cv.imshow("Cropped", cv.resize(cropped_image, (1000, 600)))
        cv.waitKey(0)
    # Show cropped image
    if show:
        cv.imshow("Cropped", cv.resize(cropped_image, (1000, 600)))
        cv.waitKey(0)
    # Save cropped image
    if save:
        out_path = f"{SOURCE_PATH}{OBJECT_NAME}/cropped/{OBJECT_NAME}_" + image_path[-7:]
        cv.imwrite(out_path, cropped_image)

        # Copy metadata from original image to cropped image
        in_metadata = pyexiv2.Image(image_path)
        out_metadata = pyexiv2.Image(out_path)
        out_metadata.modify_exif(in_metadata.read_exif())

    return cropped_image

# Usage
SOURCE_PATH = "C:/Users/v.philippoz/Documents/scanner3D/"
OBJECT_NAME = "etau_1812"
IMAGE_COUNT = 120
files = []
for i in range(IMAGE_COUNT):
    path = f"{SOURCE_PATH}{OBJECT_NAME}/{OBJECT_NAME}_" + "{:03d}.jpg".format(i+1)
    files.append(path)

# Create output directory
if not os.path.exists(f"{SOURCE_PATH}{OBJECT_NAME}/cropped/"):
    os.makedirs(f"{SOURCE_PATH}{OBJECT_NAME}/cropped/")

# Get desired image size
img_shape = cv.imread(f"{SOURCE_PATH}{OBJECT_NAME}/{OBJECT_NAME}_merged.jpg").shape[:2]
print("Image shape:", img_shape)

# Crop images
cropped_images = crop_images(files, img_shape, debug=False, show=False, save=True)