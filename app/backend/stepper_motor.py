import RPi.GPIO as GPIO
import time
import warnings
from constants import SCREW_PITCH
from threading import Thread


# Define motor class
class StepperMotor:
    def __init__(self, pinout: dict, speed: float = 180, step_per_revolution: int = 200, resolution: int = 8) -> None:
        """
        Stepper motor.

        -pinout: dict of the pinout for the stepper motor driver. Board numbers of the Raspberry Pi 4, not GPIO numbers !
        -speed: speed of rotation [deg/s]. Default = 180
        -resolution: motor step size. [1, 2, 4, 8]. Default = 8
        -step_per_revolution: full steps per revolution of the stepper motor. Default = 200
        """
        # Save args
        self._resolution = resolution
        self._step_per_revolution = float(step_per_revolution) 
        self._step_time = 1.0/self._deg2step(abs(speed))
        self.pinout = pinout
        self.step_cnt = 0
        self._clockwise = True
        self._target_steps = 0

        # Set GPIOs
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup((self.pinout['STEP'], self.pinout['DIR'], self.pinout['nSLEEP'], self.pinout['MS1'], self.pinout['MS2']), GPIO.OUT)
        GPIO.setwarnings(True)
        GPIO.output((self.pinout['nSLEEP'], self.pinout['DIR']), GPIO.HIGH)
        GPIO.output(self.pinout['STEP'], GPIO.LOW)
        available_resolutions = [1, 2, 4, 8]
        if self._resolution not in available_resolutions:
            warnings.warn(f"Incorrect argument for 'resolution': {self._resolution} was given, but only {available_resolutions} are accepted.\nUsed 'eighth'.")
            self._resolution = 8
        if self._resolution == 1:
            GPIO.output((self.pinout['MS1'], self.pinout['MS2']), GPIO.LOW)
        if self._resolution == 2:
            GPIO.output(self.pinout['MS1'], GPIO.HIGH)
            GPIO.output(self.pinout['MS2'], GPIO.LOW)
        if self._resolution == 4:
            GPIO.output(self.pinout['MS2'], GPIO.HIGH)
            GPIO.output(self.pinout['MS1'], GPIO.LOW)
        if self._resolution == 8:
            GPIO.output((self.pinout['MS1'], self.pinout['MS2']), GPIO.HIGH)

        # Start thread
        self.main_thd = Thread(target=self._run, daemon=True)
        self.main_thd.start()
    
    def get_step_time(self) -> float:
        return self._step_time

    def set_step_time(self, step_time) -> None:
        self._step_time = step_time

    def get_speed(self) -> float:
        return 1.0/self._step2deg(self._step_time)

    def set_speed(self, speed: float) -> None:
        self._step_time = 1.0/self._deg2step(abs(speed))
    
    def set_target_position(self, angle: float):
        """
        Setting this position will make the motor turn. This is the prefered way of controlling the motor.
        """
        self._target_steps = self._deg2step(angle)

    def rotate(self, angle: float) -> None:
        '''
        Make the motor turn by a specified angle. This is not suited for background tasks (threads).
        '''
        self.set_rotation_direction(clockwise=(angle < 0))
        nb_steps = self._deg2step(abs(angle))
        for _ in range(int(nb_steps)):
            self._one_step()
    
    def set_rotation_direction(self, clockwise: bool) -> None:
        if clockwise:
            GPIO.output(self.pinout['DIR'], GPIO.HIGH)
            self._clockwise = True
        else:
            GPIO.output(self.pinout['DIR'], GPIO.LOW)
            self._clockwise = False

    def _step2deg(self, steps: int):
        return steps*360.0/(self._step_per_revolution*self._resolution)
    
    def _deg2step(self, deg: float):
        return int(deg*self._step_per_revolution*self._resolution/360.0)

    def _one_step(self) -> None:
        GPIO.output(self.pinout['STEP'], GPIO.HIGH)
        time.sleep(self._step_time)
        GPIO.output(self.pinout['STEP'], GPIO.LOW)
        time.sleep(self._step_time)
        self.step_cnt += 2*int(self._clockwise) - 1
    
    def _run(self):
        while True:
            if self._target_steps > 0 and not self._clockwise:
                self._one_step()
                self._target_steps -= 1
            elif self._target_steps > 0 and self._clockwise:
                self.set_rotation_direction(clockwise=True)
                self._one_step()
                self._target_steps -= 1
            elif self._target_steps < 0 and self._clockwise:
                self._one_step()
                self._target_steps += 1
            elif self._target_steps < 0 and not self._clockwise:
                self.set_rotation_direction(clockwise=False)
                self._one_step()
                self._target_steps += 1
            else:
                time.sleep(2*self._step_time)
                continue


class CameraAxis(StepperMotor):
    def __init__(self, pinout: dict, speed: float = 180, step_per_revolution: int = 200, resolution: int = 8):
        """
        Stepper motor of the camera axis.

        -pinout: dict of the pinout for the stepper motor driver. Board numbers of the Raspberry Pi 4, not GPIO numbers !
        -speed: speed of translation [mm/s]. Default = 10
        -resolution: motor step size. [1, 2, 4, 8]. Default = 8
        -step_per_revolution: full steps per revolution of the stepper motor. Default = 200
        """
        self.translation_speed = speed
        super().__init__(pinout=pinout, resolution=resolution, step_per_revolution=step_per_revolution, speed=self.translation_speed/SCREW_PITCH) 
    
    def rotate(self, distance: float):
        angle = distance/SCREW_PITCH
        super().rotate(angle=angle)

    def get_speed(self) -> float:
        return SCREW_PITCH/self._step2deg(self._step_time)

    def set_speed(self, speed: float) -> None:
        self._step_time = SCREW_PITCH/self._deg2step(speed)
    
    def set_target_position(self, distance: float):
        """
        Setting this position will make the motor turn. This is the prefered way of controlling the motor.
        """
        angle = distance/SCREW_PITCH
        self._target_steps = self._deg2step(angle)


if __name__ == '__main__':
    import argparse
    import app.backend.MP6500_pinout as MP6500_pinout

    parser = argparse.ArgumentParser(description='Test code to make the stepper motor turn.')
    parser.add_argument('--angle', dest='angle', default=90, type=float,
                        help='angle to turn (default: 360 (1 turn))')
    parser.add_argument('--speed_r', dest='speed_r', default=36, type=float,
                        help='rotation speed in degrees per second (default: 36)')
    parser.add_argument('--dist', dest='distance', default=10, type=int,
                        help="Distance to go up fo the camera. (default: 10)")
    parser.add_argument('--speed_t', dest='speed_t', default=30, type=int,
                        help='Translation speed in mm per second (default: 30)')
    parser.add_argument('--res', dest='resolution', default=8, type=int,
                        help="motor resolution in steps. [1, 2, 4, 8] (default: 8)")
    parser.add_argument('--axis', dest='axis', default=2, type=int,
                        help="Which axis to control. 0 == turntable, 1 == camera, 2 == both. (default: 2)")
    args = vars(parser.parse_args())
    
    # Create stepper objects
    stepper_turntable = StepperMotor(pinout=MP6500_pinout.TURNTABLE, speed=args['speed_r'], resolution=args['resolution'])
    stepper_cam = CameraAxis(pinout=MP6500_pinout.CAMERA, speed=args['speed_t'], resolution=args['resolution'])


    # Basic motor tests
    print('Testing with .rotate')
    if args['axis'] == 0 or args['axis'] == 2:
        stepper_turntable.rotate(angle=args['angle'])
    if args['axis'] == 1 or args['axis'] == 2:
        stepper_cam.rotate(distance=args['distance'])


    time.sleep(1)
    print('Testing with internal threads')
    if args['axis'] == 0 or args['axis'] == 2:
        stepper_turntable.set_target_position(angle=args['angle'])
    if args['axis'] == 1 or args['axis'] == 2:
        stepper_cam.set_target_position(distance=args['distance'])
    # simulate another task
    while abs(stepper_turntable._target_steps) > 0 or abs(stepper_cam._target_steps) > 0:
        time.sleep(0.1)
        continue

    print('Done !')
    

    exit()