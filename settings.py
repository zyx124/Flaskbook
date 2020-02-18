import os

cur_dir = os.getcwd()

SECRET_KEY = 'you_will_never_guess'
DEBUG = True
MONGODB_DB = 'flaskbook'
HOSTNAME = 'http://0.0.0.0:5000'
UPLOAD_FOLDER = cur_dir + '/static/images'
STATIC_IMAGE_URL = 'images'