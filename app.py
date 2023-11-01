# .env Configuration Loading
import os
from dotenv import load_dotenv

load_dotenv()

def handle_error(e):
    print(e)
    return "Error!"

# GeoJSON Imports
from geojson import Point

# MongoDB Imports
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Settings - URL
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))

db = 0

# Check Ping
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Choose the database
    db = client.codeutsava

except Exception as e:
    handle_error(e)


# Model Imports
import pandas as pd
import cv2
import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *
import argparse
import numpy as np
from appSettings import classNames, myColor, my_map, useCuda

# Loading Model Name from .env & Initializing Model
modelName = os.getenv('MODEL_NAME')
print('Using Model:', modelName)

model = YOLO(modelName)
if useCuda:
    model.to('cuda')


# Flask Imports

import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, session
from flask_session import Session
from werkzeug.utils import secure_filename


# Image Upload Config
UPLOAD_FOLDER = 'imguploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Starting flask

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

sess = Session()
sess.init_app(app)

app.debug = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Flask Routes

@app.route("/")
def index():
    return "Server is live!"

@app.route("/potholes", methods=["GET"])
def send_pothole_data():
    pass

# Handle File Upload and Download

@app.route('/uploads/<path:filename>')
def download_file(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    # print(os.path.join(uploads, filename))
    return send_from_directory(uploads, filename)

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            # This contains the data sent from frontend
            try:
                print("Latitude:", request.form['lat'])
                print("Longitude:", request.form['lon'])
            except Exception as e:
                return handle_error(e)
            
            # Run Inference and save output
            try:
                # file.save(os.path.join(uploads, filename))
                filestr = request.files['file'].read()
                # file_bytes = np.fromstring(filestr, np.uint8)
                nparr = np.fromstring(filestr, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
                results = model(img, stream=True)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        # Bounding Box
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,255),3)
                        w, h = x2 - x1, y2 - y1
                        # cvzone.cornerRect(img, (x1, y1, w, h))

                        # Confidence
                        conf = math.ceil((box.conf[0] * 100)) / 100

                        # Class Name
                        cls = int(box.cls[0])
                        currentClass = classNames[cls]
                        # print(currentClass)

                        if conf>0.25:

                            # cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                            #   (max(0, x1), max(35, y1-10)), scale=2, thickness=2,colorB=myColor,
                                            #   colorT=(255,255,255),colorR=myColor, offset=5)
                            cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 2)
                            # currentArray = np.array([x1, y1, x2, y2, conf])
                            # detections = np.vstack((detections, currentArray))
                cv2.imwrite(os.path.join(app.root_path, "/static_detect", filename, img))
                print('Write Success:', "static_detect/"+filename)
            except Exception as e:
                return handle_error(e)
            
            return {"pothole":"true"}
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# Image Filters
def denoise_image(image):
    # Apply Non-Local Means Denoising
    denoised_image = cv2.fastNlMeansDenoising(image, None, h=10, searchWindowSize=21, templateWindowSize=7)
    return denoised_image


def convert_to_grayscale(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image
