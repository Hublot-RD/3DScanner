from constants import LEDS_PINOUT, FLASH_PIN
import RPi.GPIO as GPIO
from app.backend.led_ctrl import play_startup_sequence


GPIO.setmode(GPIO.BOARD)
GPIO.setup((FLASH_PIN, *LEDS_PINOUT.values()), GPIO.OUT)

play_startup_sequence(capture_pin=LEDS_PINOUT['CAPTURE'], error_pin=LEDS_PINOUT['ERROR'], flash_pin=FLASH_PIN)


exit()

