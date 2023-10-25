import RPi.GPIO as GPIO
import time
from threading import Thread, Event


class LED_Controller():
    def __init__(self, pin: int, state: bool = False, reversed: bool = False):
        '''
        Create LED controller class. The GPIO pin must already be configured as output.

        :param pin: The GPIO pin number.
        :param state: The initial state of the LED. True = ON, False = OFF.
        :param reversed: If True, the LED is ON when the GPIO pin is LOW. If False, the LED is ON when the GPIO pin is HIGH.
        '''
        # Public objects
        self.pin = pin
        self.state = state
        self.reversed = reversed

        # Private objects
        self._flicker_thd = Thread()
        self._flicker_thd_stop_event = Event()

        # Set GPIO pin as output
        GPIO.setup(self.pin, GPIO.OUT)

    def set_state(self, on: bool) -> None:
        '''
        Set the state of the LED.

        :param on: True = ON, False = OFF.
        '''
        self.state = on
        if (self.reversed and on) or (not self.reversed and not on):
            GPIO.output(self.pin, GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.HIGH)
    
    def toggle(self) -> None:
        '''
        Toggle the state of the LED. If the LED is ON, it will be turned OFF and vice versa.
        '''
        self.set_state(not self.state)

    def start_flicker(self, period : float = 0.2, duty_cycle: float = 0.5):
        '''
        Start flickering the LED. The flickering will continue until stop_flicker() is called.

        :param period: The period of the flickering in seconds.
        :param duty_cycle: The duty cycle of the flickering. A value of 0.5 means that the LED will be ON for half of the period and OFF for the other half.
        '''
        duty_cycle %= 1 # map duty cycle to a real number in [0.0 , 1.0]

        if not self._flicker_thd.is_alive():
            self._flicker_thd_stop_event.clear()
            self._flicker_thd = Thread(target=self._flicker, kwargs={'stop_event': self._flicker_thd_stop_event, 'period' : period, 'duty_cycle': duty_cycle})
            self._flicker_thd.start()
    
    def stop_flicker(self):
        '''
        Stop flickering the LED. It has not effect if the LED is not flickering.
        '''
        if self._flicker_thd.is_alive():
            self._flicker_thd_stop_event.set()

    def _flicker(self, stop_event: Event(), period, duty_cycle):
        while not stop_event.is_set():
            self.set_state(True)
            time.sleep(period*duty_cycle)
            self.set_state(False)
            time.sleep(period*(1-duty_cycle))


def play_startup_sequence(capture_pin: int, error_pin: int, flash_pin: int) -> None:
    """
    Play the LED startup sequence. The GPIO pins must already be configured as output.

    :param capture_pin: The GPIO pin number of the capture LED.
    :param error_pin: The GPIO pin number of the error LED.
    :param flash_pin: The GPIO pin number of the flash LED.
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