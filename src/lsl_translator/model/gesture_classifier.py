from xgboost import XGBClassifier

class GestureClassifier:
    MODEL_SAVE_PATH = "src/lsl_translator/model/gesture_classifier.pkl"

    def __init__(self) -> None:
        self.model = XGBClassifier()
        self.model.load_model(self.MODEL_SAVE_PATH)

    def predict(self, landmarks):
        return self.model.predict(landmarks)