import threading
import multiprocessing
from multiprocessing import Queue

import numpy as np
import pandas as pd

from hybrid_learning_model import HybridLearningClassifier


class Classify(multiprocessing.Process):  #threading.Thread):
    def __init__(self, queue: Queue, anotherqueue: Queue):
        super().__init__()
        self.aQueue = queue
        self.bQueue = anotherqueue

        # Call learning model to predict class
        self.hl = HybridLearningClassifier()

    def run(self):
        while True:
            if not self.aQueue.empty():
                self.classify_capture(self.aQueue.get())

    def classify_capture(self, frames):  # TODO  create function from normalisation part
        empty_list = []
        # Convert the str represented list to an actual list again
        for i, frame in enumerate(frames):
            df = pd.DataFrame(frame)
            # Recording the wrist coordinate of the first frame of each sequence.
            if i == 0:
                reference_x = df["X"][0]
                reference_y = df["Y"][0]
                reference_z = df["Z"][0]
            df["X"] = df["X"] - reference_x
            df["X"] = df["X"] - df["X"].mean()
            df["Y"] = df["Y"] - reference_y
            df["Y"] = df["Y"] - df["Y"].mean()
            df["Z"] = df["Z"] - reference_z
            df["Z"] = df["Z"] - df["Z"].mean()

            empty_list.append(df)

        # pad all with zeros to the frame size 60
        while len(empty_list) < 40:
            empty_list.append(pd.DataFrame(np.zeros((21, 3))))

        data_array = np.asarray(empty_list)

        data = self.hl.predict_data(data_array)
        self.bQueue.put(data)
        return data
