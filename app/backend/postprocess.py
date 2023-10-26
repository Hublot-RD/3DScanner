import cv2
import numpy as np

def create_circular_kernel(size):
    radius = size[0] // 2
    y, x = np.ogrid[:size[0], :size[1]]
    circular_kernel = (x - radius)**2 + (y - radius)**2 <= radius**2
    return circular_kernel.astype(np.uint8)

def create_mask(image1_path, image2_path) -> np.ndarray:
    # Load the image
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    # Convert the image to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Blur the two images to remove noise
    kernel_size = (127, 127)
    blur1 = cv2.GaussianBlur(gray1, kernel_size, 0)
    blur2 = cv2.GaussianBlur(gray2, kernel_size, 0)

    # Absolute difference
    dif = cv2.absdiff(blur1, blur2)

    # Threshold
    _, mask = cv2.threshold(dif, thresh=1, maxval=255, type=cv2.THRESH_BINARY_INV )

    for i in range(10):
        kernel = create_circular_kernel((11+2*i, 11+2*i))
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = cv2.erode(mask, kernel, iterations=1)
        # cv2.imshow("iteration "+str(i+1), cv2.resize(mask, (1000, 600)))

    # Merge regions with one final dilation
    kernel_erode = create_circular_kernel((127, 127))
    kernel_dilate = create_circular_kernel((11, 11))
    mask = cv2.erode(mask, kernel_erode, iterations=1)
    mask = cv2.dilate(mask, kernel_dilate, iterations=1)
    cv2.imshow("Mask", cv2.resize(mask, (1000, 600)))

    # Invert mask
    mask = cv2.bitwise_not(mask)

    # Convert mask to 3-channel image
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return mask

# Usage
mask = create_mask("C:/Users/v.philippoz/Documents/scanner3D/pot2/pot_001.jpg", "C:/Users/v.philippoz/Documents/scanner3D/pot2/pot_002.jpg")
for i in range(10):
    path = "C:/Users/v.philippoz/Documents/scanner3D/pot2/pot_{:03d}.jpg".format(i+1)
    tmp_img = cv2.imread(path)
    cv2.imshow("Before "+str(i+1), cv2.resize(tmp_img, (1000, 600)))
    result_image = cv2.bitwise_and(tmp_img, mask)
    cv2.imshow("Result "+str(i+1), cv2.resize(result_image, (1000, 600)))
    

cv2.waitKey(0)
cv2.destroyAllWindows()