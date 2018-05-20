#########################
# Redis Broker Settings #
#########################

REDIS_BROKER_URL = 'redis://localhost:6379/0'

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
MINIO_ACCESS_KEY = 'abcd'
MINIO_SECRET_KEY = '123abc456'

###############################
# motion_handler.py settings #
###############################

HANDLER_LOG_PATH = '/var/log/motion/motion_handler.py.log'
MOTION_SAVE_DIR = '/var/lib/motion'
HANDLER_LOG_INFO = True
HANDLER_LOG_DEBUG = False
HANDLER_MAX_UPLOAD_ATTEMPTS = 4
