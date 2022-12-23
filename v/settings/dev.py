from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=7-!@j&cdc^(+iaft@%fpuyo+q3hs+d2c)!$ys&bx(6gn7(^s9'

if DEBUG:
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vbusiness',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Vijayverma@2003'
    }
}
