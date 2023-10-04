import RPi.GPIO as GPIO
import time
from threading import Thread, Event


class LED_Controller():
    def __init__(self, pin: int, state: bool = False, reversed: bool = False):
        # Public objects
        self.pin = pin
        self.state = state
        self.reversed = reversed

        # Private objects
        self._flicker_thd = Thread()
        self._flicker_thd_stop_event = Event()

    def set_state(self, on: bool):
        self.state = on
        if (self.reversed and on) or (not self.reversed and not on):
            GPIO.output(self.pin, GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.HIGH)
    
    def toggle(self):
        self.set_state(not self.state)

    def start_flicker(self, period : float = 0.2):
        if not self._flicker_thd.is_alive():
            self._flicker_thd_stop_event.clear()
            self._flicker_thd = Thread(target=self._flicker, kwargs={'stop_event': self._flicker_thd_stop_event, 'period' : period})
            self._flicker_thd.start()
    
    def stop_flicker(self):
        self._flicker_thd_stop_event.set()

    def _flicker(self, stop_event: Event(), period : float = 0.2):
        while not stop_event.is_set():
            self.toggle()
            time.sleep(period/2)
            self.toggle()
            time.sleep(period/2)


def play_startup_sequence(capture_pin: int, error_pin: int, flash_pin: int) -> None:
    """
    Play the LED startup sequence. The GPIO pins must already be configured as output.
    """
    LED_capture = LED_Controller(pin=capture_pin, reversed=True)
    LED_error = LED_Controller(pin=error_pin, reversed=True)
    flash = LED_Controller(pin=flash_pin)

    # Turn ON all signals
    flash.set_state(True)
    LED_capture.set_state(True)
    LED_error.set_state(True)
    time.sleep(3)

    # Make capture LED flicker
    LED_capture.start_flicker()
    time.sleep(3)
    LED_capture.stop_flicker()

    # Turn OFF all signals
    LED_error.set_state(False)
    flash.set_state(False)
    LED_capture.set_state(False)

    return