from flask import Flask, jsonify, request
import numpy as np
import traceback
import cv2 as cv
from lsl_translator.utils import MediaPipe
from lsl_translator.model import SymbolClassifier
from lsl_translator.model import SymbolClassifierOld
from lsl_translator.model import GestureClassifier
from lsl_translator.model import GestureClassifierOld

app = Flask(__name__)

@app.route('/')
def home():
    return ('Hello House!')

@app.route('/predict', methods=['POST'])
def predict():
    model = SymbolClassifier()
    # model = SymbolClassifierOld()
    mp = MediaPipe()

    if model:
        try:
            file = request.files['image']
            filestr = file.read()
            file_bytes = np.frombuffer(filestr, np.uint8)       # was .fromstring
            image = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)

            image = cv.rotate(image, cv.ROTATE_180)  # PLATFORM DEPENDENT FIX LATER
            # cv.imshow("test", image)
            # cv.waitKey(0)

            multi_hand_landmarks = mp.get_multi_hand_landmarks(image)

            if multi_hand_landmarks is not None:
                pred_landmarks = np.array(multi_hand_landmarks
                                          )
                # pred_landmarks = pred_landmarks.reshape(1, -1)       # FOR OLD MODEL

                pred, confidence = model.predict_confidence(pred_landmarks)

                return jsonify({'prediction': int(pred), 'confidence' : float(confidence)})
            else:
                return jsonify({'prediction': -1})
        except:        
            return jsonify({'trace': traceback.format_exc(), 'prediction':-1})
    else:
        return ('No model here to use')
    

@app.route('/predict_gesture', methods=['POST'])
def predict_gesture():
    model = GestureClassifier()
    # model = GestureClassifierOld()
    mp = MediaPipe()

    if model:
        try:
            files = request.files.getlist('image')
            # file_data = [file.read() for file in files]
            if not files:
                return jsonify({'error': 'No files received'}), 400
             
            filestrs = [file.read() for file in files]
            file_bytes = [np.frombuffer(filestr, np.uint8) for filestr in filestrs]
            images = [cv.imdecode(file_byte, cv.IMREAD_UNCHANGED) for file_byte in file_bytes]
            
            
            for i in range(0, len(images)):
                images[i] = cv.rotate(images[i], cv.ROTATE_90_CLOCKWISE)
                cv.imwrite(f"images_{i}.jpg", images[i])

            gesture_landmarks = mp.get_multi_hand_landmarks_gesture(images)

            if gesture_landmarks is not None:
                pred_landmarks = np.array(gesture_landmarks)
                # pred_landmarks = pred_landmarks.reshape(1, -1)
                pred, confidence = model.predict_confidence(pred_landmarks)

                return jsonify({'prediction': int(pred), 'confidence' : float(confidence)})
            else:
                return jsonify({'prediction': -1})
        except:        
            return jsonify({'trace': traceback.format_exc(), 'prediction':-1})
    else:
        return ('No model here to use')
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
