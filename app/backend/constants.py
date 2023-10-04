LEDS_PINOUT = {'CAPTURE' : 5,
               'ERROR' : 3,
               }
FLASH_PIN = 13

MOTOR_TURNTABLE_PINOUT = {}
MOTOR_CAMERA_PINOUT = {}

SCREW_PITCH = 8/360 # [mm/°] Pitch of the screw used for the camera axis


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
PREVIEW_IMAGE_PATH = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/preview.jpg'
HIGHRES_IMAGE_FOLDER = '/home/pi/scanner3d/3DScanner/app/static/cam_imgs/highres/'

