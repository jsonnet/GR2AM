from flask import render_template, Flask, Response
import cv2
import platform
from os.path import abspath, dirname
from pathlib import Path
import json

from src.utils.dataclass import GestureMetaData
from src.gesture_capturing import GestureCapture

app = Flask(__name__)


@app.route("/")
def index():
    with open("static/js/captured_gestures.json") as jsonFile:
        gestures = json.load(jsonFile)
        jsonFile.close()

    with open("static/js/gesture_application_mapping.json") as jsonFile:
        mappings = json.load(jsonFile)
        jsonFile.close()

    with open("static/js/available_applications.json") as jsonFile:
        apps = json.load(jsonFile)
        jsonFile.close()

    return render_template("home_page.html", gestures=gestures, mappings=mappings, apps=apps)


@app.route("/add_gesture")
def add_gesture():

    with open("static/js/captured_gestures.json") as jsonFile:
        captures = json.load(jsonFile)
        jsonFile.close()

    with open("static/js/available_gestures.json") as jsonFile:
        gestures = json.load(jsonFile)
        jsonFile.close()

    return render_template("generating_model_capturing_data.html", captures=captures, gestures=gestures)


@app.route('/video_feed/<gesture_name>')
def video_feed(gesture_name):
    gestureMetaData = GestureMetaData(gesture_name=gesture_name)

    # Source: https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00
    if platform.system() == "Darwin":  # for mac input 1 is the camera
        gesture = GestureCapture(folder_location=str(path), gesture_meta_data=gestureMetaData, camera_input_value=1)
    else:
        gesture = GestureCapture(folder_location=str(path), gesture_meta_data=gestureMetaData, camera_input_value=0)
    return Response(gesture.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    parent_directory = dirname(dirname(dirname(abspath(__file__))))
    print(parent_directory)
    parent_directory = Path(parent_directory)
    path = parent_directory / "flask_trial_gestures"
    app.run(debug= True)
