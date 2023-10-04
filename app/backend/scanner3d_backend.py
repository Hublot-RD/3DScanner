from threading import Thread, Event
from time import sleep
from app.backend.constants import INITIAL_STATUS

class Scanner3D_backend():
    def __init__(self) -> None:
        # Create Thread related objects
        self._main_thd_stop = Event()
        self.stop_image_event = Event()
        self._main_thd_obj = Thread()
        self.image_thread_obj = Thread()

        # Set initial status
        self.status = INITIAL_STATUS


        # Play LED animation

        # Start the camera

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
        self.status = INITIAL_STATUS

    def get_status(self) -> str:
        return self.status
    
    def refresh_image(self) -> None:
        return
    
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
            sleep(0.3)

        # Closing thread properly
        print('main_thread is closing')

        

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
        self.status = {k: info[k] if k in info else v for k, v in self.status.items()}
