import RPi.GPIO as GPIO
import time


class LED_Controller():
    def __init__(self, pin: int, state: bool = False, reversed: bool = False):
        self.pin = pin
        self.state = state
        self.reversed = reversed

    def set_state(self, on: bool):
        self.state = on
        if (self.reversed and on) or (not self.reversed and not on):
            GPIO.output(self.pin, GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.HIGH)
    
    def toggle(self):
        self.set_state(not self.state)

    def start_flicker(self, duration: float = 3, period : float = 0.2):
        start_time = time.perf_counter()

        while(time.perf_counter() < start_time+duration):
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
    LED_capture.start_flicker(duration=3)

    # Turn OFF all signals
    flash.set_state(False)
    LED_capture.set_state(False)
    LED_error.set_state(False)

    return