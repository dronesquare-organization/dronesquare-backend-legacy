from .settings import *

config_secret_deploy = json.loads(open(CONFIG_SECRET_DEPLOY_FILE).read())

DB_CONFIG = config_secret_deploy['django']['db']

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

DEBUG = True
ALLOWED_HOSTS = config_secret_deploy['django']['allowed_hosts']