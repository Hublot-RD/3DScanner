from picamera2 import Picamera2
from time import sleep
from os import remove, mkdir
from os.path import isdir
from glob import glob
try:
    from app.backend.usb_interface import USBStorage
    from app.backend.constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH
except:
    from usb_interface import USBStorage
    from constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH



class Camera():
    def __init__(self, object_name: str, usb_storage: USBStorage) -> None:
        self._cam = Picamera2()
        self._preview_mode = True
        self.highres_img_cnt = 1
        self._previous_preview_path = None
        self._usb_storage = usb_storage
        self._object_name = object_name

        self._set_preview_mode(self._preview_mode)
        if not self._cam.started:
            self._cam.start()

        # Delete all existing preview images
        for filename in glob(PREVIEW_IMAGE_PATH +"preview_*"):
            remove(filename)
    
    def __del__(self) -> None:
        self._cam.close()
        del(self._cam)

    def capture_highres(self) -> dict:
        '''
        Captures a high resolution image and saves it both on the RPi and the USB storage.
        '''
        self._set_preview_mode(False)
        name = self._object_name + '_{0:03}.jpg'.format(self.highres_img_cnt)
        self.highres_img_cnt += 1
        path = HIGHRES_IMAGE_PATH + self._object_name + '/' 
        if not isdir(path):
            mkdir(path)
        metadata = self._cam.capture_file(path+name)
        if self._usb_storage is not None:
            dest_folder = self._usb_storage.loc + self._object_name + '/'
            if not isdir(dest_folder):
                mkdir(dest_folder)
            self._usb_storage.copy_file_to(file_path=path+name, dest_folder=dest_folder)
        return metadata
    
    def capture_preview(self, name: str) -> dict:
        # delete previous preview image
        if self._previous_preview_path is not None:
            remove(self._previous_preview_path)
        self._set_preview_mode(True)
        metadata = self._cam.capture_file(PREVIEW_IMAGE_PATH + name + '.jpg')
        self._previous_preview_path = PREVIEW_IMAGE_PATH + name + '.jpg'
        return metadata
    
    def reset(self) -> None:
        self.highres_img_cnt = 1
        self._set_preview_mode(True)
    
    def _set_preview_mode(self, preview_ON: bool) -> None:
        if not self._preview_mode and preview_ON:
            if self._cam.started:
                self._cam.stop()
            self._cam.still_configuration.size = CAMERA_RESOLUTION_PREVIEW
            self._cam.configure('still')
            self._cam.start()
            sleep(1)
        elif self._preview_mode and not preview_ON:
            if self._cam.started:
                self._cam.stop()
            self._cam.still_configuration.size = CAMERA_RESOLUTION_HIGHRES
            self._cam.configure('still')
            self._cam.start()
            sleep(1)
        self._preview_mode = preview_ON


if __name__ == "__main__":
    my_cam = Camera(object_name='test', usb_storage=USBStorage(loc='/media/pi/INTENSO/'))
    my_cam.capture_preview(name='ma_photo')
    print('success')
    my_cam.reset()
    meta = my_cam.capture_highres()
    print(meta)

    exit()
    
