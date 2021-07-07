import sys

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, confusion_matrix

from dl import CNN1D_Classifier as CNN1D
from dl.deep_learning_model import DeepLearningClassifier
from learning_model_class import LearningModel
from machine_learning_working.get_classifier import Classifier
from machine_learning_working.machine_learning_model import MachineLearningClassifier
from machine_learning_working.predict import Predict
from utils import format_data_for_nn as ft, read_data as rd


class HybridLearningClassifier(LearningModel):

    def __init__(self):
        self.ml = MachineLearningClassifier(extracted_features_path="machine_learning_working/training_features_josh.joblib")
        self.dl = DeepLearningClassifier()

    def predict_data(self, data):
        result_dl, acc_dl = self.dl.predict_data(data)
        result_ml = self.ml.predict_data(data)

        # TODO could we do a combined score instead?
        if acc_dl < 0.85:
            print("ML")
            return result_ml[0]
        else:
            print("DL")
            return int(result_dl)

    def train_model(self):
        pass
