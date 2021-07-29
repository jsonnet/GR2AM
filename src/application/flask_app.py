import json
from os.path import abspath, dirname
from pathlib import Path

from flask import Flask, Response, redirect, render_template, request, session, url_for

from application.config import config
from application.controller import home_page, record_gesture

app = Flask(__name__)
app.register_blueprint(record_gesture.bp)
app.register_blueprint(home_page.bp)

app.secret_key = b'DUMMYKEY'

"""API that returns the index page with captured getures,
 available applications and application_gesture mapping"""


@app.route("/", methods=['GET', 'POST'])
def index():
    init()
    if request.method == 'POST':
        print(request)
        print(request.form)

    elif request.method == 'GET':
        pass
    with open("static/js/captured_gestures.json") as jsonFile:
        captured_gestures = json.load(jsonFile)
        jsonFile.close()

        # Map

    with open("static/js/gesture_application_mapping.json") as jsonFile:
        mappings = json.load(jsonFile)
        jsonFile.close()

    with open("static/js/available_applications.json") as jsonFile:
        apps = json.load(jsonFile)
        jsonFile.close()

    return render_template("home_page.html", gestures=captured_gestures, mappings=mappings, apps=apps)


@app.route("/login", methods=["POST"])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


def init():
    """Read the folder where the gestures are recorded and accordingly update the
    captured_gestures.json file."""

    # FIXME this mess needs to be fixed don't use the files names from metaData!!!!!!

    parent_directory = dirname(dirname(dirname(abspath(__file__))))
    parent_directory = Path(parent_directory)
    path = parent_directory / config.GESTURE_FOLDER_NAME / "MetaData.json"
    with open(path, "r") as jsonFile:
        recorded_gestures_dict = json.load(jsonFile)
        jsonFile.close()

    recorded_gesture_names = list(recorded_gestures_dict.keys())

    # Map with the correct names

    with open("static/js/captured_gestures.json", "r") as jsonFile:
        gestures_gifs = json.load(jsonFile)
        jsonFile.close()

    gestures_gifs.clear()
    for ele in recorded_gesture_names:
        # print(recorded_gestures_dict[ele])
        if recorded_gestures_dict[ele]["trials"] > config.THRESHOLD_TRIALS:
            gestures_gifs[ele] = "./static/img/{}.gif".format(ele.lower())

    with open("static/js/captured_gestures.json", "w") as jsonFile:
        json.dump(gestures_gifs, jsonFile)
        jsonFile.close()



if __name__ == "__main__":
    app.run(debug=True)
