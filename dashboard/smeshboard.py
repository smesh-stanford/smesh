from flask import Flask, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) # enable CORS for Flask to respond to React app's requests on different port

@app.route('/')
def home():
    return "<p>Welcome to SMeshboard's Flask backend server!</p>"

@app.get('/get-data')
def send_data():
    data_path = os.path.join(app.root_path, 'static', '4004_pmsa003i.csv')
    return send_file(data_path, mimetype='text/csv')

if __name__ == '__main__':
    app.run()