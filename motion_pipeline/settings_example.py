#########################
# Redis Broker Settings #
#########################

REDIS_BROKER_URL = 'redis://192.168.0.24:6379/0'
SIMPLECACHE_KEY_PREFIX = 'simplecache/'

#####################
# Database Settings #
#####################

DB_CONNSTRING = 'mysql+pymysql://user:pass@host:3306/DbName?charset=utf8mb4'

###############################
# S3 / Minio Storage Settings #
###############################

BUCKET_NAME = 'some_name'
BUCKET_PREFIX = 'motion/'

#: If using Minio <https://www.minio.io/> instead of S3, set MINIO_URL to the
#: minio endpoint URL (i.e. 'http://192.168.0.1:9000') and set the
#: MINIO_ACCESS_KEY and MINIO_SECRET_KEY settings. If using S3, leave MINIO_URL
#: as None. When using S3, credentials will be retrieved using the normal
#: cross-SDK methods used by boto3, and the MINIO key settings are ignored.
MINIO_URL = 'http://192.168.0.24:9000'
MINIO_ACCESS_KEY = 'zzzzzzzzzzzzzzzzzzzz'
MINIO_SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

#: If the minio storage directory is reachable from the web and worker hosts
#: or containers, set it here and files from minio will be read directly from
#: this path (as the bucket root) instead of downloaded. Otherwise, set to None.
MINIO_LOCAL_MOUNTPOINT = '/mnt/minio/some_name/motion'

#############################
# Image Processing Settings #
#############################

THUMBNAIL_MAX_SIZE = 640, 640

#########################
# Notification Settings #
#########################

PUSHOVER_API_KEY = 'PushOverKeyXxxxxxxxxxxxxxxxxxx'
PUSHOVER_USER_KEY = 'uXxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PUSHOVER_SEND_EMERGENCY = True
PUSHOVER_RETRY = True

#: The base URL to use for links to the web UI in notifications. Specified
#: manually here in case you're running on a dynamic IP, NATted, etc.
#: This must end in a trailing slash.
NOTIFICATION_BASE_URL = 'http://foo.example.com/'

###############################
# motion_handler.py settings #
###############################

HANDLER_LOG_PATH = '/var/log/motion/motion_handler.py.log'
MOTION_SAVE_DIR = '/var/lib/motion'
HANDLER_LOG_INFO = True
HANDLER_LOG_DEBUG = False
HANDLER_MAX_UPLOAD_ATTEMPTS = 4

##############################
# Camera settings #
##############################

CAM_USER = 'MyUser'
CAM_PASS = 'MyPass'

CAMERAS = {
    'CAM1': {
        'mjpeg_url': '/cam1/cgi-bin/mjpg/video.cgi?channel=1&subtype=1',
        'snapshot_url': '/cam1/cgi-bin/snapshot.cgi?channel=0',
        'rstp_url': 'rtsp://%s:%s@192.168.0.61:80/cam/realmonitor?channel=1&subtype=0&proto=Dahua3' % (CAM_USER, CAM_PASS),
        'control_info': {
            'control_type': 'Amcrest',
            'control_user': CAM_USER,
            'control_pass': CAM_PASS,
            'control_base_url': 'http://192.168.0.61:80/',
            'control_presets': {
                '1': 'One',
                '2': 'Two',
                '3': 'Three',
                '4': 'Four',
                '5': '5',
                '6': '6',
                '7': '7',
                '8': '8',
                '9': '9'
            }
        },
        'motion_host': '192.168.0.24',
        'motion_port': 8080,
        'motion_camera_id': 1
    },
    'CAM2': {
        'mjpeg_url': '/cam2/cgi-bin/mjpg/video.cgi?channel=1&subtype=1',
        'snapshot_url': '/cam2/cgi-bin/snapshot.cgi?channel=0',
        'rstp_url': 'rtsp://%s:%s@192.168.0.63:80/cam/realmonitor?channel=1&subtype=0&proto=Dahua3' % (CAM_USER, CAM_PASS),
        'control_info': None,
        'motion_host': '192.168.0.36',
        'motion_port': 8080,
        'motion_camera_id': 2
    }
}

# For development of the live view, uncommenting these makes it easier...
# CAMERAS['CAM1']['mjpeg_url'] = '/static/640x480.png'
# CAMERAS['CAM2']['mjpeg_url'] = '/static/640x480.png'
