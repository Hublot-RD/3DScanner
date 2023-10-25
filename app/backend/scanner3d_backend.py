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
from app.backend.utils import forecast_time, CaptureParameters, s2time


class Scanner3D_backend():
    def __init__(self, status_queue: Queue) -> None:
        '''
        Create a Scanner3D_backend object.

        :param status_queue: The queue used to send status updates to the frontend.
        '''
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
        '''
        Start the capture process.

        :param capture_params: The capture parameters, as a dict.
        '''
        # Start capture if not already capturing
        if not self._main_thd_obj.is_alive():
            # Save capture parameters
            self._p = CaptureParameters(capture_params)
            print(self._p)

            # Forecast capture time and number of images
            self._total_time, self._total_pics = forecast_time(self._p)
            print(s2time(self._total_time), type(s2time(self._total_time)))
            self._update_status({'time_value' : s2time(self._total_time)})

            # Create USB storage object
            if self._p.usb_storage_loc == 'Aucun':
                self._usb_storage = None
            else:
                self._usb_storage = USBStorage(name=self._p.usb_storage_loc)

            # Start the camera
            self._cam = Camera(object_name=self._p.obj_name, usb_storage=self._usb_storage)

            # Start main thread
            self._main_thd_stop.clear()
            self._main_thd_obj = Thread(target=self._main_thd_target)
            self._main_thd_obj.start()

    def stop(self) -> None:
        '''
        Stop the capture process.
        '''
        # Stop process
        self._main_thd_stop.set()
        self._main_thd_obj.join()
        
        self._status = cst.INITIAL_STATUS
        self._update_status(self._status)
        self._led_capture.set_state(on=False)
        self._led_error.set_state(on=False) # DO I REALLY WANT TO RESET ERROR ?
        self._led_flash.set_state(on=False)
        del(self._cam)
        print('Capture stopped properly')
    
    def refresh_image(self) -> str:
        '''
        Refresh preview image.
        '''
        name = 'preview_' + str(random()).split('.')[-1]
        # adding a random part to the file name ensures 
        # that the client won't have the file already cashed
        tmp_cam = Camera(object_name='preview', usb_storage=None)
        tmp_cam.capture_preview(name=name)
        del(tmp_cam)
        return name+'.jpg'
    
    def refresh_usb_list(self) -> list:
        '''
        Refresh USB devices list.
        '''
        paths = get_usb_drives_list()
        devices = [path.split('/')[-1] for path in paths]
        return devices
    
    # def _capture_photo(self) -> str:
    #     self._cam.capture_highres()
    #     return cst.HIGHRES_IMAGE_PATH
    
    def _main_thd_target(self) -> None:
        try:
            # Start blink capture LED
            self._led_capture.start_flicker()
            self._update_status({'state' : 'capture'})

            # Home the z axis
            self._mot_camera.home()
            self._update_status({'text_value' : 'Calibration de l\'axe'})

            # Apply motor speeds
            self._mot_camera.set_speed(self._p.motor_camera_speed)
            self._mot_turntable.set_speed(self._p.motor_turntable_speed)

            # Take pictures of the object
            self._update_status(info={'text_value' : 'Démarrage de la séquence'})
            self._capture_whole_object()

        except Exception as e:
            print('error detected')
            self._led_capture.stop_flicker()
            self._led_capture.set_state(on=False)
            self._led_error.set_state(True)
            self._update_status(info={'text_value' : 'Une erreur est survenue: ' + str(e),
                                      'state' : 'error'})

        else:
            if not self._main_thd_stop.is_set(): # Successful finish
                # Unmount usb storage
                self._update_status(info={'text_value' : 'Ejection du stockage USB'})
                if self._usb_storage is not None:
                    self._usb_storage.umount()


                # Stop blink capture LED, ON continuous
                self._led_capture.stop_flicker()
                sleep(self._p.pause_time)
                self._update_status(info={'text_value' : 'Capture terminée avec succès', 
                                          'progress_value' : 100,
                                          'state' : 'end'})
                self._led_capture.set_state(on=True)
            else:
                # Stop blink capture LED, OFF continuous
                self._led_capture.stop_flicker()
                self._led_capture.set_state(on=False)
                self._update_status(info={'text_value' : 'Capture interrompue',
                                          'state' : 'end'})
        finally:
            # Exit properly
            print('_main_thd closed')


    def _update_status(self, info: dict) -> None:
        self._status = {k: info[k] if k in info else v for k, v in self._status.items()}
        self._status_queue.put(self._status)

    def _capture360deg(self) -> float:
        '''
        Capture one layer of the object, all around it.
        '''
        remaining_angle = 360.0
        while (remaining_angle > self._p.motor_turntable_step) and (not self._main_thd_stop.is_set()):
            # Capture image with flash
            self._update_status(info={'text_value' : f'Capture de l\'image {self._cam.highres_img_cnt}/{self._total_pics}'})
            if self._p.flash_enabled:
                self._led_flash.set_state(True)
            self._cam.capture_highres()
            if self._p.flash_enabled:
                self._led_flash.set_state(False)

            # Move turntable
            sleep(self._p.pause_time)
            self._update_status({'progress_value' : 100*(self._cam.highres_img_cnt-1)/self._total_pics})
            self._mot_turntable.rotate(self._p.motor_turntable_step)
            remaining_angle -= self._p.motor_turntable_step
            sleep(self._p.pause_time)
        
        # Capture last image
        if not self._main_thd_stop.is_set():
            self._update_status(info={'text_value' : f'Capture de l\'image {self._cam.highres_img_cnt}/{self._total_pics}'})
            if self._p.flash_enabled:
                self._led_flash.set_state(True)
            self._cam.capture_highres()
            if self._p.flash_enabled:
                self._led_flash.set_state(False)
            sleep(self._p.pause_time)

        return remaining_angle
    
    def _capture_whole_object(self) -> None:
        '''
        Capture whole object, layer by layer.
        '''
        remaining_height = self._p.obj_height
        while (remaining_height > 0) and (not self._main_thd_stop.is_set()):
            # Take pictures all around object
            remaining_angle = self._capture360deg()
            
            if not self._main_thd_stop.is_set():
                # Move camera up and turntable to initial position
                self._update_status(info={'state' : 'Move to next height'})
                height_up = min(self._p.motor_camera_step, remaining_height)
                self._mot_camera.set_target_position(distance=height_up)
                self._mot_turntable.set_target_position(angle=remaining_angle)
                remaining_height -= height_up

                # Wait for this height to be finished
                while self._mot_camera.is_busy or self._mot_turntable.is_busy:
                    sleep(0.1)
                sleep(self._p.pause_time)
        
        # Capture last height
        if not self._main_thd_stop.is_set():
            remaining_angle = self._capture360deg()
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
