try:
    from app.backend.constants import CAPTURE_PARAMETERS_PATH, DEFAULT_CAPTURE_PARAMETERS_PATH
except:
    from constants import CAPTURE_PARAMETERS_PATH, DEFAULT_CAPTURE_PARAMETERS_PATH
from warnings import warn
import json

class CaptureParameters():
    def __init__(self, params: dict = None) -> None:
        self._default_params = self._load_parameters(DEFAULT_CAPTURE_PARAMETERS_PATH)
        if params is not None:
            self._params = params # input param dict, then is populated with all params
            self.set_from_dict(self._params)
        else:
            self.set_from_dict(self._default_params)

    def __str__(self) -> str:
        txt = 'Capture parameters:'
        for key, val in self._params.items():
            txt += f'\n- {key:<35}{val}'
        return txt

    def _get_from_dict(self, params: dict, key: str, var_type: type):
        p = params.get(key, self._default_params[key])
        if type(p) is not var_type:
            old_type = type(p)
            try:
                p = var_type(p)
            except ValueError:
                p = var_type(self._default_params[key])
                warn(f'Parameter "{key}" could not be casted from {old_type} to {var_type}. Using default value instead.', category=RuntimeWarning)
        self._params[key] = p
        return p
    
    def _load_parameters(self, path2file: str) -> dict:
        with open(path2file, 'r') as file:
            return json.load(file)
    
    def save(self, filename: str):
        with open(CAPTURE_PARAMETERS_PATH+filename+'.json', 'w') as file:
            json.dump(self._params, file)

    def set_from_dict(self, params: dict) -> None:
        # Movement parameters
        self.pause_time = self._get_from_dict(params, 'PAUSE_TIME', float)
        self.motor_camera_speed = self._get_from_dict(params, 'MOTOR_CAMERA_SPEED', float)
        self.motor_camera_step = self._get_from_dict(params, 'MOTOR_CAMERA_STEP', float)
        self.motor_turntable_speed = self._get_from_dict(params, 'MOTOR_TURNTABLE_SPEED', float)
        self.motor_turntable_step = self._get_from_dict(params, 'MOTOR_TURNTABLE_STEP', float)

        # Camera parameters
        self.camera_exposure = self._get_from_dict(params, 'CAMERA_EXPOSURE', float)
        self.camera_resolution_highres = self._get_from_dict(params, 'CAMERA_RESOLUTION_HIGHRES', tuple)
        self.camera_resolution_preview = self._get_from_dict(params, 'CAMERA_RESOLUTION_PREVIEW', tuple)
        self.flash_enabled = self._get_from_dict(params, 'FLASH_ENABLED', bool)
    
    def set_from_file(self, filename: str):
        p = self._load_parameters(CAPTURE_PARAMETERS_PATH+filename+'.json')
        self.set_from_dict(p)





def forecast_time(params: CaptureParameters):
    '''
    Forecast the total time in seconds the capture will take with given capture parameters.
    '''
    total_time = 42
    # total_time += nb_pics * (2*pause+time_pic+save_usb)
    # total_time += angle_tot * angular_speed
    # total_time += max(distance_tot * speed, remaining_angle_tot * angular_speed)
    # total_time += time_startup
    # total_time += time_closing
    return total_time


if __name__ == '__main__':
    p = CaptureParameters(params={'PAUSE_TIME': 10.0})
    print(p)
    # p.load_parameters(DEFAULT_CAPTURE_PARAMETERS_PATH)
    p.save('test')
    p.set_from_file('test')
    print(p)