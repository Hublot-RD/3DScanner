import numpy as np
import cv2 as cv
import glob


grid_size = (9, 6)
square_size = 27.0 # mm

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((grid_size[0]*grid_size[1],3), np.float32)
objp[:,:2] = np.mgrid[0:grid_size[0],0:grid_size[1]].T.reshape(-1,2) * square_size

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# search for images in ../static/cam_imgs/highres/test/
images = glob.glob("C:\\Users\\v.philippoz\\Documents\\scanner3D\\chessboard1.jpg")

print(images)
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, grid_size, None)
    print(ret)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, grid_size, corners2, ret)
        cv.imshow('img', cv.resize(img, (1000, 600)))
        cv.waitKey(0)

        # Get camera parameters
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print("Camera matrix:\n", mtx)
        print("Distortion coefficients: ", dist.ravel())


cv.destroyAllWindows()