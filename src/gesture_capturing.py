import io
import json
import os
from multiprocessing import Queue
from pathlib import Path
from typing import NamedTuple

import cv2
import mediapipe as mp

from src.utils.dataclass import GestureMetaData


class GestureCapture:
    def __init__(self, camera_input_value: int, folder_location: str = "", gesture_meta_data: GestureMetaData = None,
                 aQueue: Queue = None, cQueue: Queue = None, window_size=30):
        self.gesture_name = None
        self.gesture_path = None
        self.all_keypoints = []
        self.live_framesize = window_size

        self.camera_input_value = camera_input_value
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

        if gesture_meta_data is not None:
            self.gestureMetaData = gesture_meta_data
            self.folder_location = folder_location
            self.meta_data_file = str(Path(self.folder_location) / "MetaData.json")

            if not (os.path.isfile(self.meta_data_file) and os.access(self.meta_data_file, os.R_OK)):
                with io.open(self.meta_data_file, 'w') as db_file:
                    db_file.write(json.dumps({}))
            with open(self.meta_data_file) as file:
                self.gesture_dict = json.load(file)
            self.live = False
            self.preventRecord = False
        else:
            self.live = True
            self.preventRecord = True

        self.aQueue = aQueue
        self.cQueue = cQueue

        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
    def on_press(self,key):
        self.key_capture = key
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def setup_cap(self):
        if not (self.gestureMetaData.gestureName in self.gesture_dict.keys()):
            self.gesture_dict[self.gestureMetaData.gestureName] = self.gestureMetaData.__dict__
        self.gesture_name = self.gestureMetaData.gestureName + '_' + str(
            self.gesture_dict[self.gestureMetaData.gestureName]["trials"] + 1) + '.txt'
        self.gesture_path = self.folder_location + '/' + self.gesture_name

        print(self.gesture_name)

    def get_frame(self):
        # Setup for right file to be recorded
        if not self.live:
            self.setup_cap()

        cap = cv2.VideoCapture(self.camera_input_value)
        # cap = cv2.VideoCapture('/Users/jsonnet/OneDrive/Studium/PyCom/LumosNox/HandDataset/raw3.mp4')
        last_result = ""

        record, redo, end = False, False, False
        frame_count =0
        while cap.isOpened() and not end:

            frame_count+=1
            # result stores the hand points extracted from mediapipe
            _, image = cap.read()
            image = cv2.flip(image, 1)  # mirror invert camera image

            # Record frames to all_keypoints
            if record or self.live:
                self.record_frame(image)

            # Display mark to indicate file over length
            if record and len(self.all_keypoints) >= self.live_framesize:
                cv2.putText(image, "!", (150, 100), cv2.QT_FONT_NORMAL, 2, (0, 0, 255, 255), 2)

            # Collect results from classifying process
            if self.cQueue and not self.cQueue.empty():
                last_result = str(self.cQueue.get())

            if last_result:  # If a result is present display it
                cv2.putText(image, "Last class: " + self.translate_class(last_result), (10, 50), cv2.QT_FONT_NORMAL, 1,
                            (0, 0, 255, 255), 2)  # BGR of course

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

            #cv2.imshow('MediaPipe Hands', image)

            # Keyboard bindings #
            k = cv2.waitKey(1)  # read key pressed event
            try:
                if k == '-1':
                    pass  # no key press (don't waste time)
                elif (k % 256 == 32) or (self.key_capture.char == 's'):  # spacebar to record
                    if not self.preventRecord:
                        record = not record
                        print("Toggle Recording Mode")
                    else:
                        self.live = True
                if k & 0xFF == ord('q'):  # close on key q
                    record = False
                    self.write_file()
                    end = True
                elif k & 0xFF == ord('n') or (self.key_capture.char == 'n'):  # next capture
                    record = False
                    self.write_file()
                    self.setup_cap()
                elif k & 0xFF == ord('r') or (self.key_capture.char == 'r'):  # redo capture
                    record = False
                    self.all_keypoints = []
            except AttributeError:
                pass  # TODO figure this one out

        # After the loop release the cap object
        cap.release()

        # Destroy all the windows
        cv2.destroyAllWindows()

    def get_hand_points(self, image) -> NamedTuple("res", [('multi_hand_landmarks', list), ('multi_handedness', list)]):
        with self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.7) as hands:
            # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to pass by reference.
            image.flags.writeable = False
            results = hands.process(image)
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            return results

    def record_frame(self, image):
        # Get hand joints using MediaPipe
        results = self.get_hand_points(image)
        # Display the resulting frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        keypoints_per_frame = []
        if results.multi_hand_landmarks:
            for data_point in results.multi_hand_landmarks[0].landmark:
                if data_point:
                    keypoints_per_frame.append({
                        'X': data_point.x,
                        'Y': data_point.y,
                        'Z': data_point.z,
                    })
        if keypoints_per_frame:
            if self.aQueue:
                self.aQueue.put(keypoints_per_frame)
            else:
                self.all_keypoints.append(keypoints_per_frame)

    def write_file(self):
        if self.all_keypoints and not self.live:  # only do smth when we have data to write
            with open(self.gesture_path, "w") as data_file:  # open file and save/close afterwards
                # data_file.write(dimensions)
                for item in self.all_keypoints:  # write all frames
                    data_file.write(str(item) + "\n")

            self.update_meta_data(self.gesture_dict, self.gesture_name)  # update the meta file
            self.all_keypoints = []

    def update_meta_data(self, gesture_dictionary, gesture_file):
        gesture_dictionary[self.gestureMetaData.gestureName]["trials"] += 1
        gesture_dictionary[self.gestureMetaData.gestureName]["files"].append(gesture_file)
        with open(self.meta_data_file, "w") as outfile:
            json.dump(gesture_dictionary, outfile)

    @staticmethod
    def translate_class(classid: str) -> str:
        if not classid.isdigit():
            print("wats dat?!" + classid)
            return ''
        classid = int(classid)

        classes = {0: 'Thumb tap', 1: 'Thumb Swipe Up', 2: 'Thumb Swipe Down',
                   3: 'Index tap', 4: 'Index Swipe Up', 5: 'Index Swipe Down',
                   6: 'Middle tap', 7: 'Middle Swipe Up', 8: 'Middle Swipe Down',
                   9: 'Ring tap', 10: 'Ring Swipe Up', 11: 'Ring Swipe Down',
                   12: 'Little tap', 13: 'Little Swipe Up', 14: 'Little Swipe Down',
                   15: 'Negative_still', 16: 'Negative_up', 17: 'Negative_down'}

        return classes[classid]
