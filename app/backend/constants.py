# Physical constants
LEDS_PINOUT = {'CAPTURE' : 5,
               'ERROR' : 3,
               }
FLASH_PIN = 13
MOTOR_TURNTABLE_PINOUT = {'STEP' : 36,
                        'DIR' : 38,
                        'nSLEEP' : 40,
                        'MS1' : 32,
                        'MS2' : 31,
                        }
MOTOR_CAMERA_PINOUT = {'STEP' : 33,
                        'DIR' : 35,
                        'nSLEEP' : 37,
                        'MS1' : 32,
                        'MS2' : 31,
                        'HOMING_SWITCH_PIN' : 26, 
                        }

SCREW_PITCH = 8/360 # [mm/°] Pitch of the screw used for the camera axis


# Default fallback values
INITIAL_STATUS = {'state': 'ready',
                  'progress_value': 0,
                  'text_value': '',
                  'time_value': '00m 00s'
                  }
CAMERA_RESOLUTION_HIGHRES = (4608, 2592)
CAMERA_RESOLUTION_PREVIEW = (576, 324)

PREVIEW_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/'
HIGHRES_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/highres/'
CAPTURE_PARAMETERS_PATH = '/home/pi/scanner3d/3DScanner/app/backend/capture_parameter_sets/'
DEFAULT_CAPTURE_PARAMETERS_PATH = CAPTURE_PARAMETERS_PATH + 'default.json'
