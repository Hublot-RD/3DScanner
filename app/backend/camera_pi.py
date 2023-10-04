from picamera2 import Picamera2
from time import sleep
from constants import CAMERA_RESOLUTION


# with Picamera2() as camera:
#     # camera.resolution = (64,64)
#     camera.exposure_mode = 'night' # to have minimal gain so less noise
#     # camera.flash_mode = 'on' # look here to make it work: https://picamera.readthedocs.io/en/release-1.13/api_camera.html?highlight=exposure_mode#picamera.PiCamera.flash_mode
    
#     # give time to camera to set properly exposure, iso etc ...
#     sleep(2)
    
#     for i in range(int(5/5)):
#         sleep(5)
#         camera.capture(f'./images/img_test_{i}.jpg', format='jpeg')

#     print(f'Sensor: {camera.revision}')

class Camera():
    def __init__(self) -> None:
        self.cam = Picamera2()
        self.cam.still_configuration.size = CAMERA_RESOLUTION
        self.cam.configure('still')
        self.cam.start()
        sleep(1)

    def capture(self, path: str, name: str, img_format: str) -> None:
        metadata = self.cam.capture_file(path+name+'.'+img_format)
        return metadata





if __name__ == "__main__":
    my_cam = Camera()
    meta = my_cam.capture(path='/home/pi/scanner3d/3DScanner/app/static/cam_imgs/', 
                          name='test1', img_format='jpg')
    print(meta)
    exit()
    
