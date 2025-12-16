"""
Django settings for bdshopping project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-np%bs_w=&5a429#9=jq4&3_^0=rkt2%4=lu+hl7b0c^2v0t117'

DEBUG = os.environ.get('DEBUG', 'True') == 'True'  # লোকালে True, production-এ False

# লোকাল development-এর জন্য
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    # Production-এর জন্য
    ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']
    
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    
    # Our Apps
    'home',
    'accounts',
    'payments',
    'products',
    'cart',
    'orders',
    'coupons',
    'wishlist',
    'reviews',
    'analytics',
]

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email Configuration (Optional)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For testing
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # For production
# Payment settings
PAYMENT_SUCCESS_URL = '/payments/success/'
PAYMENT_FAILURE_URL = '/payments/failed/'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bdshopping.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_total',
            ],
        },
    },
]

WSGI_APPLICATION = 'bdshopping.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Create media folders if not exists
MEDIA_FOLDERS = [
    'media/profile_pics',
    'media/products',
]

for folder in MEDIA_FOLDERS:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
    
# Login/Logout URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Session settings for cart
CART_SESSION_ID = 'cart'


# File upload settings for Termux
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Disable file locking in Termux
import django.core.files.locks

# Monkey patch to disable file locking
def no_lock(fd, flags):
    return True

def no_unlock(fd):
    return True

django.core.files.locks.lock = no_lock
django.core.files.locks.unlock = no_unlock

# Ensure Pillow is installed
try:
    from PIL import Image
except ImportError:
    print("Warning: Pillow is not installed. Run: pip install Pillow")
    
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'