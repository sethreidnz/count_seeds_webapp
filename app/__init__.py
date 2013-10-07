from flask import Flask
from werkzeug import secure_filename
from settings import APP_UPLOADS




app = Flask(__name__)
from app import views
app.config['UPLOAD_FOLDER'] = APP_UPLOADS
