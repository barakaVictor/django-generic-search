import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'test-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]
SPYDER_START_URLS = {
    'gammaspider': ['http://localhost:8000/']
}

INSTALLED_APPS = [
    'generic_search',
]