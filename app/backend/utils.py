try:
    from app.backend.constants import DEFAULT_CAPTURE_PARAMETERS
except:
    from constants import DEFAULT_CAPTURE_PARAMETERS
from warnings import warn

class CaptureParameters():
    def __init__(self, params: dict) -> None:
        self._params = params # input param dict, then is populated with all params

        # Movement parameters
        self.pause_time = self._get_from_params('PAUSE_TIME', float)
        self.motor_camera_speed = self._get_from_params('MOTOR_CAMERA_SPEED', float)
        self.motor_camera_step = self._get_from_params('MOTOR_CAMERA_STEP', float)
        self.motor_turntable_speed = self._get_from_params('MOTOR_TURNTABLE_SPEED', float)
        self.motor_turntable_step = self._get_from_params('MOTOR_TURNTABLE_STEP', float)

        # Camera parameters
        self.camera_exposure = self._get_from_params('CAMERA_EXPOSURE', float)
        self.camera_resolution_highres = self._get_from_params('CAMERA_RESOLUTION_HIGHRES', tuple)
        self.camera_resolution_preview = self._get_from_params('CAMERA_RESOLUTION_PREVIEW', tuple)
        self.flash_enabled = self._get_from_params('FLASH_ENABLED', bool)


    def _get_from_params(self, key: str, var_type: type):
        p = self._params.get(key, DEFAULT_CAPTURE_PARAMETERS[key])
        if type(p) is not var_type:
            old_type = type(p)
            try:
                p = var_type(p)
                warn(f'Parameter "{key}" was automatically casted from {old_type} to {var_type}.', category=RuntimeWarning)
            except ValueError:
                p = DEFAULT_CAPTURE_PARAMETERS[key]
                warn(f'Parameter "{key}" could not be casted from {old_type} to {var_type}. Using default value instead.', category=RuntimeWarning)
        self._params[key] = p
        return p
    
    def __repr__(self) -> str:
        txt = 'Capture parameters:'
        for key, val in self._params.items():
            txt += f'\n- {key:<35}{val}'
        return txt




def forecast_time(params: CaptureParameters):
    '''
    Forecast the total time in seconds the capture will take with given capture parameters.
    '''
    total_time = 0
    # total_time += nb_pics * (2*pause+time_pic+save_usb)
    # total_time += angle_tot * angular_speed
    # total_time += max(distance_tot * speed, remaining_angle_tot * angular_speed)
    # total_time += time_startup
    # total_time += time_closing
    return total_time


if __name__ == '__main__':
    p = CaptureParameters(params={'PAUSE_TIME': 10.0})
    print(p)