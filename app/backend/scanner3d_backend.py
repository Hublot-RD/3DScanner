from threading import Thread, Event
from queue import Queue
import RPi.GPIO as GPIO
from time import sleep
from random import random
import app.backend.constants as cst 
from app.backend.camera_pi import Camera
from app.backend.led_ctrl import LED_Controller, play_startup_sequence
from app.backend.stepper_motor import StepperMotor, CameraAxis
from app.backend.usb_interface import USBStorage, get_usb_drives_list


class Scanner3D_backend():
    def __init__(self, status_queue: Queue) -> None:
        # Set GPIO mode to board for retro and future compatibility
        GPIO.setmode(GPIO.BOARD)
        
        # Create Thread related objects
        self._main_thd_stop = Event()
        self.stop_image_event = Event()
        self._main_thd_obj = Thread()
        self.image_thread_obj = Thread()

        # Queue
        self._status_queue = status_queue

        # Set initial status
        self._status = cst.INITIAL_STATUS

        # Create motor objects
        self._mot_turntable = StepperMotor(pinout=cst.MOTOR_TURNTABLE_PINOUT)
        self._mot_camera = CameraAxis(pinout=cst.MOTOR_CAMERA_PINOUT)

        # Create LEDs objects
        self._led_flash = LED_Controller(cst.FLASH_PIN)
        self._led_capture = LED_Controller(cst.LEDS_PINOUT['CAPTURE'], reversed=True)
        self._led_error = LED_Controller(cst.LEDS_PINOUT['ERROR'], reversed=True)

        # Play LED animation
        # play_startup_sequence(capture_pin=self._led_capture.pin, error_pin=self._led_error.pin, flash_pin=self._led_flash.pin)
        # sleep(1)


    def start(self, capture_params: dict) -> None:
        # Start capture if not already capturing
        if not self._main_thd_obj.is_alive():
            # Save capture parameters
            self._obj_height = float(capture_params['height'])
            self._obj_detail = capture_params['detail']
            self._obj_name = capture_params['obj_name']

            print('Object name:', self._obj_name)
            print('Object height:', self._obj_height)
            print('Object details level:', self._obj_detail)

            # Create USB storage object
            if capture_params['usb_storage_loc'] == 'Aucun':
                self._usb_storage = None
            else:
                self._usb_storage = USBStorage(name=capture_params['usb_storage_loc'])

            # Start the camera
            self._cam = Camera(object_name=self._obj_name, usb_storage=self._usb_storage)

            # Start main thread
            self._main_thd_stop.clear()
            self._main_thread_obj = Thread(target=self._main_thd_target)
            self._main_thread_obj.start()

    def stop(self) -> None:
        # Stop process
        self._main_thd_stop.set()
        
        self._status = cst.INITIAL_STATUS
        self._led_capture.set_state(on=False)
        self._led_error.set_state(on=False) # DO I REALLY WANT TO RESET ERROR ?
        self._led_flash.set_state(on=False)
        del(self._cam)
    
    def refresh_image(self) -> str:
        name = 'preview_' + str(random()).split('.')[-1]
        # adding a random part to the file name ensures 
        # that the clien won't have the file already cashed
        tmp_cam = Camera(object_name='preview', usb_storage=None)
        tmp_cam.capture_preview(name=name)
        del(tmp_cam)
        return name+'.jpg'
    
    def refresh_usb_list(self) -> list:
        paths = get_usb_drives_list()
        devices = [path.split('/')[-1] for path in paths]
        return devices
    
    # def _capture_photo(self) -> str:
    #     self._cam.capture_highres()
    #     return cst.HIGHRES_IMAGE_PATH
    
    def _main_thd_target(self) -> None:
        print('\nCapture started')     

        # Start blink capture LED
        self._led_capture.start_flicker()

        # Home the z axis
        # self._mot_camera.home()

        # Take pictures of the object
        self._capture_whole_object(height_increment=42, rotation_increment=350)

        if not self._main_thd_stop.is_set(): # Successful finish
            # Umount usb storage
            if self._usb_storage is not None:
                self._usb_storage.umount()

            # Stop blink capture LED, ON continuous
            self._led_capture.stop_flicker()
            sleep(cst.PAUSE_IMAGES_MOTOR)
            self._led_capture.set_state(on=True)
        else:
            # Stop blink capture LED, OFF continuous
            self._led_capture.stop_flicker()
            self._led_capture.set_state(on=False)

        # Exit properly
        print('_main_thd closed')

    def _update_status(self, info: dict) -> None:
        self._status = {k: info[k] if k in info else v for k, v in self._status.items()}
        self._status_queue.put(self._status)

    def _capture360deg(self, rotation_increment: float) -> float:
        remaining_angle = 360.0
        # print('remaining_angle', remaining_angle)
        while (remaining_angle >= rotation_increment) and (not self._main_thd_stop.is_set()):
            # Capture image with flash
            self._led_flash.set_state(True)
            self._cam.capture_highres()
            self._led_flash.set_state(False)

            # Move turntable
            sleep(cst.PAUSE_IMAGES_MOTOR)
            self._mot_turntable.rotate(rotation_increment)
            remaining_angle -= rotation_increment
            # print('remaining_angle', remaining_angle)
            sleep(cst.PAUSE_IMAGES_MOTOR)
        
        # Capture last image
        if not self._main_thd_stop.is_set():
            self._led_flash.set_state(True)
            self._cam.capture_highres()
            self._led_flash.set_state(False)
            sleep(cst.PAUSE_IMAGES_MOTOR)

        return remaining_angle
    
    def _capture_whole_object(self, height_increment: float, rotation_increment: float) -> None:
        remaining_height = 10*self._obj_height # cm to mm
        while remaining_height > 0:
            # Take pictures all around object
            remaining_angle = self._capture360deg(rotation_increment=rotation_increment)
            
            if not self._main_thd_stop.is_set():
                # Move camera up and turntable to initial position
                height_up = min(height_increment, remaining_height)
                self._mot_camera.set_target_position(distance=height_up)
                self._mot_turntable.set_target_position(angle=remaining_angle)
                remaining_height -= height_up

                # Wait for this height to be finished
                while self._mot_camera.is_busy or self._mot_turntable.is_busy:
                    sleep(0.1)
                sleep(cst.PAUSE_IMAGES_MOTOR)
        
        # Capture last height
        if not self._main_thd_stop.is_set():
            remaining_angle = self._capture360deg(rotation_increment=rotation_increment)
            self._mot_turntable.set_target_position(angle=remaining_angle)
        



            

if __name__ == '__main__':
    from time import sleep
    status_queue = Queue()
    backend = Scanner3D_backend(status_queue=status_queue)
    sleep(2)
    print('Refreshing preview')
    file_path = backend.refresh_image()
    # file = backend.capture_photo()
    print('success image')
    sleep(0.5)
