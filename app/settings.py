#settings.py for app settings
import os
# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_UPLOADS = os.path.join(APP_STATIC, 'uploads')
APP_ANALYSED = os.path.join(APP_UPLOADS, 'analysed')
