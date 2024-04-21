from xgboost import XGBClassifier

class SymbolClassifier:
    MODEL_SAVE_PATH = "src/lsl_translator/model/symbol_classifier.pkl"

    def __init__(self) -> None:
        self.model = XGBClassifier()
        self.model.load_model(self.MODEL_SAVE_PATH)

    def predict(self, landmarks):
        return self.model.predict(landmarks)