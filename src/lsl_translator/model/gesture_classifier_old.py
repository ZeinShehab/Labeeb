from xgboost import XGBClassifier

class GestureClassifierOld:
    MODEL_SAVE_PATH = "src/lsl_translator/model/gesture_classifier.pkl"

    def __init__(self) -> None:
        self.model = XGBClassifier()
        self.model.load_model(self.MODEL_SAVE_PATH)

    def predict(self, landmarks):
        return self.model.predict(landmarks)
    
    def predict_confidence(self, landmarks):
        pred_proba = self.model.predict_proba(landmarks)
        pred_proba = pred_proba[0]
        # pred = np.argmax(pred_proba)
        pred = 0.0
        confidence = 0.0
        for i in range(len(pred_proba)):
            if pred_proba[i] > confidence:
                pred = i
                confidence = pred_proba[i]

        return [pred, confidence]