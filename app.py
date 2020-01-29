#Usage: python app.py
import os
 
from flask import render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename
import argparse
import time
import uuid
import base64
import os
import requests
import numpy as np
from os import listdir
from os.path import isfile, join
import soundfile as sf
from python_speech_features import mfcc
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten, Dropout
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from keras.models import model_from_json
from keras.models import Sequential,model_from_json

UPLOAD_FOLDER = 'uploads'

url = "https://www.fast2sms.com/dev/bulk"
headers = {
 'authorization': "vijZsnUAxX1NmTElCFfu0QWwa8zd3pbSR6I2VOHPrtyqG9koL7LZoiYp01D2EWc8vklwOPIzUqfmgN6A",
 'Content-Type': "application/x-www-form-urlencoded",
 'Cache-Control': "no-cache",
 }




def predict1(audiofile):
    with open('Audioclass.json', 'r') as f:
        mymodel=model_from_json(f.read())
    mymodel.load_weights("audio.h5")

    s,r=sf.read(audiofile)
    #print(len(s.shape))
    if len(s.shape)==2:
        s=s[0,:]
    #print(len(s.shape))
    x=np.mean(mfcc(s,r, numcep=12,nfft=2048),axis=0)
    x = x.reshape(1,12)
    y = mymodel.predict(x)
    y = int(y.round())

    return y


def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def template_test():
    return render_template('template.html', label='', imagesource='../uploads/template.jpg')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("Upload")
        import time
        start_time = time.time()
        file = request.files['file']
        print(file.filename)
     
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(file_path)
        result = predict1(file_path)
        if result==1:
            msg="Baby needs immediate attention"		
        if result==0:
            msg="NO"    
        print(file_path)
        filename = my_random_string(6) + filename

        os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("--- %s seconds ---" % str (time.time() - start_time))
        payload = "sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers=9963611235"
        response = requests.request("POST", url, data=payload, headers=headers)
 
        print(response.text)
        return render_template('template.html',label=msg )
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=False
    app.run(host='0.0.0.0', port=3000)
