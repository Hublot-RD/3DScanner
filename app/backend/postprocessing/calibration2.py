import cv2 as cv
import glob
import numpy as np
# import matplotlib.pyplot as plt


def calibrate_camera(images_folder):
    images_names = glob.glob(images_folder)
    
    images = []
    for imname in images_names:
        im = cv.imread(imname, 1)
        images.append(im)
 
    # plt.figure(figsize = (10,10))
    # ax = [plt.subplot(2,2,i+1) for i in range(4)]
    #
    # for a, frame in zip(ax, images):
    #     a.imshow(frame[:,:,[2,1,0]])
    #     a.set_xticklabels([])
    #     a.set_yticklabels([])
    # plt.subplots_adjust(wspace=0, hspace=0)
    # plt.show()
 
    #criteria used by checkerboard pattern detector.
    #Change this if the code can't find the checkerboard
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
    rows = 9 #number of checkerboard rows.
    columns = 6 #number of checkerboard columns.
    world_scaling = 27 #change this to the real world square size in mm
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    #frame dimensions. Frames should be the same size.
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
    for i,frame in enumerate(images):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
 
        #find the checkerboard
        ret, corners = cv.findChessboardCorners(gray, (rows, columns), None)
       
        if ret == True:
 
            #Convolution size used to improve corner detection. Don't make this too large.
            conv_size = (11, 11)
 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            print("i=", i)
            # if side=="left":
            #     # if i==0 or i==1:
            #     #     corners=np.flipud(corners)
            #     pass
            # else:
            #     if i==0 or i==2 :
            #         corners=np.flipud(corners)

            cv.drawChessboardCorners(frame, (rows,columns), corners, ret)
            cv.namedWindow("img",cv.WINDOW_NORMAL)
            cv.imshow("img", frame)
            cv.waitKey(500)
 
            objpoints.append(objp)
            imgpoints.append(corners)
 
 
    # print("COUCOU",len(imgpoints))
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    tot_error=0
    total_points=0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        # imgpoints2=imgpoints2.reshape(-1,2)
        tot_error+=np.sum(np.abs(imgpoints[i]-imgpoints2)**2)
        print(np.sum(np.abs(imgpoints[i]-imgpoints2)**2))
        total_points+=len(objpoints[i])

    print("RMSE",np.sqrt(tot_error/total_points))
    print('rmse:', ret)
    print('camera matrix:\n', mtx)
    print('distortion coeffs:', dist)
    print('Rs:\n', rvecs)
    print('Ts:\n', tvecs)
 
    return mtx, dist, tvecs


mtx, dist, Ts = calibrate_camera(images_folder='C:\\Users\\v.philippoz\\Documents\\scanner3D\\calibration\\*')


# np.save("K_L",mtx1)
# np.save("K_R",mtx2)
# np.save("R_C_L",R)
# np.save("T_C_L",T)
# np.save("dl",dist1)
# np.save("dr",dist2)