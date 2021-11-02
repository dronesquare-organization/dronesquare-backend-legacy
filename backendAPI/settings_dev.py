from .settings import *

config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

DB_CONFIG = config_secret_debug['django']['db']

DATABASES = {
    'default': {
        'ENGINE': DB_CONFIG['engine'],
        'NAME': DB_CONFIG['name'],
        'USER': DB_CONFIG['user'],
        'PASSWORD': DB_CONFIG['password'],
        'HOST': DB_CONFIG['host'],
        'PORT': DB_CONFIG['port'],
        'OPTIONS': {
            'sslmode': 'disable',
         },
    }
}

# LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'myLog.log')
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             'datefmt': "%d/%b/%Y %H:%M:%S"
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': LOG_FILE,
#             'formatter': 'verbose',
#             'maxBytes': 1024 * 1024 * 10,
#             'backupCount': 5,
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'propagate': True,
#             'level': 'INFO',
#         },
#         'django.request': {
#             'handlers': ['file'],
#             'propagate': False,
#             'level': 'INFO',
#         },
#         'users': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#         },
#         'projects': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#         }
#     }
# }

DEBUG = True
ALLOWED_HOSTS = config_secret_debug['django']['allowed_hosts']
