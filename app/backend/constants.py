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
INITIAL_STATUS = {'state': 'Idle',
                  'progress_value': 0,
                  'text_value': '',
                  }

PREVIEW_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/'
HIGHRES_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/highres/'

DEFAULT_CAPTURE_PARAMETERS = {'PAUSE_TIME' : 1.0, #[s] Pause time between a movement of a motor and taking a picture
                              'MOTOR_CAMERA_SPEED' : 10.0, #[mm/s]
                              'MOTOR_CAMERA_STEP' : 20.0, #[mm]
                              'MOTOR_TURNTABLE_SPEED' : 45.0, #[deg/s]
                              'MOTOR_TURNTABLE_STEP' : 15.0, #[deg]
                              'CAMERA_EXPOSURE' : 42.0, #[us]
                              'CAMERA_RESOLUTION_HIGHRES' : (4608,2592), #[pixel]
                              'CAMERA_RESOLUTION_PREVIEW' : (576, 324), #[pixel]
                              'FLASH_ENABLED' : True,
                              }
