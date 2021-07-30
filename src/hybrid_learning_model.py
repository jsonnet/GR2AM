import logging

from dl.deep_learning_model import DeepLearningClassifier
from learning_model_class import LearningModel
from machine_learning_working.machine_learning_model import MachineLearningClassifier


class HybridLearningClassifier(LearningModel):

    def __init__(self, window_size=40):
        self.window_size = window_size

        self.ml = MachineLearningClassifier(already_trained_classifier="trained_model.joblib", window_size=self.window_size)
        self.dl = DeepLearningClassifier(window_size=self.window_size, output_size=18)

    def predict_data(self, data):
        # result_dl, acc_dl = self.dl.predict_data(data)
        result_ml, acc_ml = self.ml.predict_data(data)

        print("RESULT--> DL: " + str(result_dl) + ' Confi:' + str(acc_dl) + " ML: " + str(result_ml) + ' Confi:' + str(acc_ml))
        # print("RESULT--> ML: " + str(result_ml) + ' Confidence:' + str(acc_ml))
        if acc_dl < 0.85:
            print("ML" + str(result_ml) + " " + str(acc_ml))
            return result_ml
        else:
            print("DL: " + str(result_dl))
        return int(result_dl)
        # return result_ml

    def train_model(self):
        pass
