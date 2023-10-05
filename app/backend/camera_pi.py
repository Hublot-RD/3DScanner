from picamera2 import Picamera2
from time import sleep
from os import remove
from glob import glob
from app.backend.constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH
# from constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_FOLDER


class Camera():
    def __init__(self) -> None:
        self._cam = Picamera2()
        self._preview_mode = True
        self._highres_img_cnt = 0
        self._previous_preview_path = None

        self._set_preview_mode(self._preview_mode)
        if not self._cam.started:
            self._cam.start()

        # Delete all existing preview images
        for filename in glob(PREVIEW_IMAGE_PATH +"preview_*"):
            remove(filename)

    def capture_highres(self) -> dict:
        self._set_preview_mode(False)
        name = 'img_{0:03}.jpg'.format(self._highres_img_cnt)
        self._highres_img_cnt += 1
        metadata = self._cam.capture_file(HIGHRES_IMAGE_PATH + name)
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
        self._highres_img_cnt = 0
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
    my_cam = Camera()
    my_cam.capture_preview()
    print('success')
    my_cam.reset()
    meta = my_cam.capture_highres()
    print(meta)

    exit()
    
