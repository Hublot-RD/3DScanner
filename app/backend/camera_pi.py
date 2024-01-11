from picamera2 import Picamera2
from libcamera import controls
from exiftool import ExifToolHelper
from time import sleep
from os import remove, mkdir
from os.path import isdir
from glob import glob
import cv2
try:
    from app.backend.usb_interface import USBStorage
    from app.backend.constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH
except ImportError:
    from usb_interface import USBStorage
    from constants import CAMERA_RESOLUTION_HIGHRES, CAMERA_RESOLUTION_PREVIEW, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH



class Camera():
    def __init__(self, object_name: str, usb_storage: USBStorage = None) -> None:
        '''
        Creates a Camera object.

        :param object_name: The name of the object that is being photographed.
        :param usb_storage: The USBStorage object that is used to store the images.
        '''
        self._cam = Picamera2()
        self._preview_mode = False # Set to false to force _set_preview_mode to apply the camera parameters
        self.highres_img_cnt = 1
        self._previous_preview_path = None
        self._usb_storage = usb_storage
        self._object_name = object_name
        the_good_mode = self._cam.sensor_modes[2]
        self._preview_config = self._cam.create_preview_configuration({"size": CAMERA_RESOLUTION_PREVIEW}, raw=the_good_mode)
        self._highres_config = self._cam.create_preview_configuration({"size": CAMERA_RESOLUTION_HIGHRES}, raw=the_good_mode)
        self._cam.align_configuration(self._preview_config)
        self._cam.align_configuration(self._highres_config)


        self._set_preview_mode(True)
        if not self._cam.started:
            self._cam.start()
        # Delete all existing preview images
        for filename in glob(PREVIEW_IMAGE_PATH +"preview_*"):
            remove(filename)
    
    def __del__(self) -> None:
        try:
            self._cam.close()
            sleep(2) # make sure the camera is closed before deleting the object
            del(self._cam)
        except AttributeError:
            # The camera was not initialised
            pass

    def capture_highres(self) -> dict:
        '''
        Captures a high resolution image and saves it both on the RPi and the USB storage.
        '''
        self._set_preview_mode(False)
        name = self._object_name + '_{0:03}.jpg'.format(self.highres_img_cnt)
        self.highres_img_cnt += 1
        path = HIGHRES_IMAGE_PATH + self._object_name + '/'
        # Make sure image path exists
        if not isdir(HIGHRES_IMAGE_PATH):
            mkdir(HIGHRES_IMAGE_PATH)
        if not isdir(path):
            mkdir(path)
        
        # Focus camera
        success = self._cam.autofocus_cycle()
        if not success:
            Warning('Autofocus failed! Continuing anyway...')
        
        # Take picture
        metadata = self._cam.capture_file(path+name)
        with ExifToolHelper() as et:
            et.set_tags(path+name, 
                        tags={"FocalLength": 2.75,
                              "FNumber": 2.2, 
                              "FocalPlaneXResolution" : 25.4/(1.4/1000), 
                              "FocalPlaneYResolution" : 25.4/(1.4/1000), 
                              "FocalPlaneResolutionUnit" : "inch"},
                        params=["-P", "-overwrite_original"])
        
        # Copy picture to USB storage
        if self._usb_storage is not None:
            dest_folder = self._usb_storage.loc + self._object_name + '/'
            if not isdir(dest_folder):
                mkdir(dest_folder)
            self._usb_storage.copy_file_to(file_path=path+name, dest_folder=dest_folder)
        return metadata
    
    def capture_preview(self, name: str) -> dict:
        '''
        Captures a low resolution image.
        '''
        # Make sure image path exists
        if not isdir(PREVIEW_IMAGE_PATH):
            mkdir(PREVIEW_IMAGE_PATH)

        # Delete previous preview image
        if self._previous_preview_path is not None:
            remove(self._previous_preview_path)
        self._set_preview_mode(True)
        success = self._cam.autofocus_cycle()
        if not success:
            Warning('Autofocus failed! Continuing anyway...')
        metadata = self._cam.capture_file(PREVIEW_IMAGE_PATH + name + '.jpg')
        self._previous_preview_path = PREVIEW_IMAGE_PATH + name + '.jpg'
        return metadata
    
    def reset(self) -> None:
        self.highres_img_cnt = 1
        self._set_preview_mode(True)

    def merge_highres(self) -> None:
        '''
        Add the last high resolution image into the merged image.
        '''
        img_id = self.highres_img_cnt - 1
        new_img_name = self._object_name + '_{0:03}.jpg'.format(img_id)
        new_img_path = HIGHRES_IMAGE_PATH + self._object_name + '/' + new_img_name
        out_path = f"{HIGHRES_IMAGE_PATH}{self._object_name}/{self._object_name}_merged.jpg"

        if img_id <= 1:
            # Initialise the merged image
            merged = cv2.imread(new_img_path)
        else:
            # Load the new image
            new_img = cv2.imread(new_img_path)

            # Load the merged image
            merged = cv2.imread(out_path)
            
            # Merge the image to get a better idea of the object boundary
            merged = cv2.addWeighted(merged, (img_id-1)/img_id, new_img, 1/img_id, 0)
        cv2.imwrite(out_path, merged)
    
    def save_merged_to_usb(self) -> None:
        '''
        Copy the merged image to the USB storage.
        '''
        if self._usb_storage is not None:
            dest_folder = self._usb_storage.loc + self._object_name + '/'
            if not isdir(dest_folder):
                mkdir(dest_folder)
            self._usb_storage.copy_file_to(file_path=HIGHRES_IMAGE_PATH + self._object_name + '/' + self._object_name + '_merged.jpg', dest_folder=dest_folder)

    
    def _set_preview_mode(self, preview_ON: bool) -> None:
        if not self._preview_mode and preview_ON:
            if self._cam.started:
                self._cam.stop()
            self._cam.configure(self._preview_config)
            self._cam.set_controls({"AeMeteringMode": controls.AeMeteringModeEnum.CentreWeighted,
                                "AeExposureMode": controls.AeExposureModeEnum.Long,
                                "AeConstraintMode": controls.AeConstraintModeEnum.Highlight,
                                })
            self._cam.start()
        elif self._preview_mode and not preview_ON:
            if self._cam.started:
                self._cam.stop()
            self._cam.configure(self._highres_config)
            self._cam.set_controls({"AeMeteringMode": controls.AeMeteringModeEnum.CentreWeighted,
                                "AeExposureMode": controls.AeExposureModeEnum.Long,
                                "AeConstraintMode": controls.AeConstraintModeEnum.Shadows,
                                })
            self._cam.start()
        self._preview_mode = preview_ON


if __name__ == "__main__":
    my_cam = Camera(object_name='test', usb_storage=None)#USBStorage(name='INTENSO'))
    # my_cam._cam.stop()
    # print(my_cam._cam.sensor_modes)
    meta = my_cam.capture_preview(name='ma_photo')
    print(meta)
    my_cam.reset()
    sleep(1)
    meta = my_cam.capture_highres()
    print(meta)

    # my_cam._cam.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": float(i)})
    # meta = my_cam._cam.capture_file(HIGHRES_IMAGE_PATH+'test/test_{0:03}.jpg'.format(1))
    # success = my_cam._cam.autofocus_cycle()
    # print('success: ', success)
    # my_cam._cam.set_controls({"AfRange": 10})
        

    exit()
    
