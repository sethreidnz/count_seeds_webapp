import os
from count_objects import contour_features as cf
from count_objects import im_proc
from settings import APP_UPLOADS, APP_STATIC, APP_ANALYSED
from flask import render_template,request, redirect, url_for, send_from_directory, jsonify
from app import app
from werkzeug import secure_filename
import cv2
import sys
import numpy as np
import uuid
import StringIO
import subprocess
from datetime import datetime


ALLOWED_EXTENSIONS = set(['bmp','jpg','png'])
global LATEST_IMAGE_PATH
LATEST_IMAGE_PATH = ""

def allowed_file(filename): #for dealing checking allowed file extentions against the defined extensions allowed
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<path:filename>') #to get an image from the upload folder
def uploaded_file(filename):
    return send_from_directory(APP_UPLOADS,filename) #to get an image from the analysed folder

@app.route('/uploads/analysed/<path:filename>') #to get an image from the analysed folder
def analysed_image(filename):
    return send_from_directory(APP_ANALYSED,filename)

@app.route('/upload_image', methods=['GET', 'POST']) #to upload an image to the server from a form post
def upload_image():
    global LATEST_IMAGE_PATH
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            LATEST_IMAGE_PATH = "uploads/" + filename

    return render_template("analyse.html", title = 'Analyse') #show the analyse image page

@app.route('/')#home
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home')

@app.route('/_get_latest_image') #a function to return the last image uploaded from a JSON get request
def get_latest_image():
        return jsonify(img_path = LATEST_IMAGE_PATH)

@app.route('/capture-image') #capture image using the built in rasperry pi raspistill application
def capture_image():
    global LATEST_IMAGE_PATH
    time = datetime.now()
    filename = "capture-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    img_path = "app/static/uploads/" + filename
    subprocess.call("raspistill -w 1296 -h 972 -t 0 -e jpg -q 15 -o %s --nopreview -n" % img_path, shell=True)
    LATEST_IMAGE_PATH = "uploads/" + filename
    return render_template("analyse.html", title = 'Analyse')

@app.route('/_count_seeds') #used to analyse the image and return certain statistics
def count_seeds():
    img_src = request.args.get('img', type=str)#get the filename from the json request
    img_src = os.path.join(APP_STATIC, img_src)#get the full path of the image
    
    img = cv2.imread(img_src,cv2.CV_LOAD_IMAGE_COLOR) #read the image into a openCV image object
    contourList = im_proc.getContourListFrom(img, initValues=False) #find all the contours
    output = im_proc.drawContoursFromList(contourList)#draw the contours onto a copy of the original image
    
    seedList = list()#to hold the seed data
    seedListHeaders = ['Seed Number','Centroid','Seed Area','Length to Width','Circularity']#the headers for the statics table

    #iterate through the contour objects and get their statistics. These statistics are put into 
    for key, cnt in contourList.iteritems():
        featureList = list()
        cnt.getCentroid()
        featureList.append(cnt.getID())
        featureList.append(cnt.getCentroid())
        featureList.append(str(cnt.getArea()))
        cnt.getBoundingBox()
        boundingBoxDims = cnt.getMinBoundingBoxDimensions()
        featureList.append(round(cnt.getContourLengthToWidth(),2))
        featureList.append(round(cnt.getHeywoodCircularity(),2))
        seedList.append(featureList)

                 
    filename = str(uuid.uuid4()) + ".jpg" #create random filename for the analysed image
    img_save_path = "app/static/uploads/analysed/" + filename #filepath for analysed image
    cv2.imwrite(img_save_path , output) #save the analysed image
    return jsonify(filename = filename, seedList = seedList, seedListHeaders = seedListHeaders)#pass jsonified data back to the client
