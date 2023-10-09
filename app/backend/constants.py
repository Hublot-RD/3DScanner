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

PAUSE_IMAGES_MOTOR = 1 # [s] Pause time between a movement of a motor and taking a picture

CAMERA_MAX_SPEED = 42 #[cm/s]
CAMERA_STEP_HEIGHT = 42 #[cm]

TURNTABLE_MAX_SPEED = 42 #[deg/s]
TURNTABLE_STEP_ANGLE = 42 #[deg]

CAMERA_EXPOSURE = 42 #[us]

FLASH_ON = True

INITIAL_STATUS = {'state': 'Idle',
                  'progress_value': 0,
                  'text_value': '',
                  }

CAMERA_RESOLUTION_HIGHRES = (4608,2592)
CAMERA_RESOLUTION_PREVIEW = (576, 324)
PREVIEW_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/'
HIGHRES_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/highres/'

