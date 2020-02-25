"""
Django settings for LogNuts project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ #環境変数をファイルから読み込む
import dj_database_url
from decimal import Decimal


env = environ.Env()
env.read_env('.env')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'lognutsapp.apps.LognutsappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4', #レスポンシブデザイン導入のため
    'storages',   #AWS S3を利用するため
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'LogNuts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins':[ 
                'bootstrap4.templatetags.bootstrap4', #レスポンシブデザイン対応
            ],
        },
    },
]

WSGI_APPLICATION = 'LogNuts.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = { 'default': dj_database_url.config() }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#ログイン画面のURL
LOGIN_URL = 'lognuts:login'
#ログイン後に遷移する画面のURL
LOGIN_REDIRECT_URL='lognuts:top'
#ログアウト後に遷移する画面のURL
LOGOUT_REDIRECT_URL='lognuts:top'

#mealsout_nuts_DBのURL
MEALSOUT_NUTS_URL= STATIC_ROOT + '/lognuts/csv/mealsout_nuts.csv'

#PFC_SCOREを決定するために使用する値の境界のURL
PFC_SCORE_SECTION_URL= STATIC_ROOT + '/lognuts/csv/pfc_score_section.csv'

#PFCのレーダーチャートのPFCの基準値
RADAR_P = Decimal(16.5)
RADAR_F = Decimal(25)
RADAR_C = Decimal(57.5)

#推薦する食品の数
FOOD_SUGGESTION_NUM = 5
#推薦に使用する食品の摂取時刻(n時間以内に食べた食品を使って推薦)
SUGGESTION_HOUR = 24

"""
栄養所要量の推奨摂取量の設定(生活運動強度が[適度]の男性の基準値)
"""
#エネルギー
ENERGIE_BORDER = 2650

#タンパク質
P_RATE_MAX = 20
P_RATE_MIN = 13
#脂質
F_RATE_MAX = 20
F_RATE_MIN = 30
#炭水化物
C_RATE_MAX = 50
C_RATE_MIN = 65

#推薦時に読み込むメニュータグリスト
MENU_TAG_LIST = [
    0,1,2,3
]

# herokuデプロイをするために追加
try:
    from .local_settings import *
except ImportError:
    pass

if not DEBUG:
    # AWSの設定
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    MEDIA_URL = S3_URL

    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    # herokuの設定
    import django_heroku
    django_heroku.settings(locals())

# herokuのロギング処理
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}