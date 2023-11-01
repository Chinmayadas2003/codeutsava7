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

# Loading Model Name from .env & Initializing Model
modelName = os.getenv('MODEL_NAME')
print('Using Model:', modelName)

model = YOLO(modelName)
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
            # Save the image and also process it as OpenCV Frame
            try:
                # file.save(os.path.join(uploads, filename))
                filestr = request.files['file'].read()
                # file_bytes = np.fromstring(filestr, np.uint8)
                nparr = np.fromstring(filestr, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
                result = model(frame, stream=True)
                for r in result:
                    print("Inference Result:", r.boxes)
                
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
