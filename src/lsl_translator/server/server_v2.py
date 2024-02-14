from flask import Flask, jsonify, request
import numpy as np
import traceback
import cv2 as cv
from xgboost import XGBClassifier
from lsl_translator.helpers import MediaPipe

app = Flask(__name__)
xgb_save_path = "../../../model/keypoint_classifier.pkl"

@app.route('/predict', methods=['POST'])
def predict():
    model = XGBClassifier()
    model.load_model(xgb_save_path)
    mp = MediaPipe()

    if model:
        try:
            file = request.files['image']
            filestr = file.read()
            file_bytes = np.fromstring(filestr, np.uint8)
            image = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)

            # image = cv.rotate(image, cv.ROTATE_90_CLOCKWISE)  # PLATFORM DEPENDENT FIX LATER

            multi_hand_landmarks = mp.get_multi_hand_landmarks(image)

            if multi_hand_landmarks is not None:
                pred_landmarks = np.array(multi_hand_landmarks)
                pred_landmarks = pred_landmarks.reshape(1, -1)
                pred = model.predict(pred_landmarks)

                return jsonify({'prediction': int(pred[0])})
            else:
                return jsonify({'prediction': -1})
        except:        
            return jsonify({'trace': traceback.format_exc(), 'prediction':-1})
    else:
        return ('No model here to use')
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
