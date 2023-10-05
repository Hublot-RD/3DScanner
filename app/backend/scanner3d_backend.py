from threading import Thread, Event
from queue import Queue
import RPi.GPIO as GPIO
from time import sleep
from random import random
from app.backend.constants import LEDS_PINOUT, FLASH_PIN, INITIAL_STATUS, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH
from app.backend.camera_pi import Camera
from app.backend.led_ctrl import play_startup_sequence
# from constants import LEDS_PINOUT, FLASH_PIN, INITIAL_STATUS, PREVIEW_IMAGE_PATH, HIGHRES_IMAGE_PATH
# from camera_pi import Camera
# from led_ctrl import play_startup_sequence


class Scanner3D_backend():
    def __init__(self, status_queue: Queue) -> None:
        # Create Thread related objects
        self._main_thd_stop = Event()
        self.stop_image_event = Event()
        self._main_thd_obj = Thread()
        self.image_thread_obj = Thread()

        # Queue
        self._status_queue = status_queue

        # Set initial status
        self._status = INITIAL_STATUS


        # Play LED animation
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup((FLASH_PIN, *LEDS_PINOUT.values()), GPIO.OUT)
        # play_startup_sequence(capture_pin=LEDS_PINOUT['CAPTURE'], error_pin=LEDS_PINOUT['ERROR'], flash_pin=FLASH_PIN)
        sleep(1)

        # Start the camera
        self.cam = Camera()


        # Home the z axis

        pass

    def start(self, capture_params: dict) -> None:
        # Start main thread
        if not self._main_thd_obj.is_alive():
            self._main_thd_stop.clear()
            main_thread_obj = Thread(target=self._main_thd_target, kwargs={'stop_event': self._main_thd_stop, 'capture_params': capture_params})
            main_thread_obj.start()

    def stop(self) -> None:
        self._main_thd_stop.set()
        self._status = INITIAL_STATUS

    # def get_status(self) -> str:
    #     return self.status
    
    def refresh_image(self) -> str:
        name = 'preview_' + str(random()).split('.')[-1]
        # adding a random part to the file name ensures 
        # that the clien won't have the file already cashed 
        self.cam.capture_preview(name=name)
        return name+'.jpg'
    
    def capture_photo(self) -> str:
        self.cam.capture_highres()
        return HIGHRES_IMAGE_PATH
    
    def _main_thd_target(self, stop_event: Event(), capture_params: dict) -> None:
        self.obj_height = capture_params['height']
        self.obj_detail = capture_params['detail']
        self.obj_name = capture_params['obj_name']

        print('\nCapture started')
        print('Object name:', self.obj_name)
        print('Object height:', self.obj_height)
        print('Object details level:', self.obj_detail)

        # Dummy function
        texts = ["Processing", "Processing.", "Processing..", "Processing..."]
        cnt = 0
        info = {'progress_value': 0, 'text_value': texts[cnt]}

        while not stop_event.is_set():
            cnt += 1
            info['progress_value'] = cnt % 101
            info['text_value'] = texts[cnt%4]
            self._update_status(info)
            sleep(0.2)

        # Closing thread properly
        print('_main_thd closed')

        

        # Start blink capture LED

        # Home the z axis

        # Repeat :

        #   Take pictures all around object

        #   Move camera up

        #   Save picture to USB stick

        # Exit properly

        # Stop blink capture LED, ON continuous

        # Wait for user restart (or see how I want to handle end of capture)

    def _update_status(self, info: dict) -> None:
        self._status = {k: info[k] if k in info else v for k, v in self._status.items()}
        self._status_queue.put(self._status)

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
