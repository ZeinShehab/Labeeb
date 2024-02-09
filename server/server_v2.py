from flask import Flask, jsonify, request
import numpy as np
import traceback
import cv2 as cv
import copy
import mediapipe as mp
app = Flask(__name__)
from xgboost import XGBClassifier
import sys
sys.path.append('C:/Users/zeins/LSL_Translator/')
from helpers.generate_keypoints import calc_landmark_list

xgb_save_path = "../model/alphabet_classifier.pkl"
# xgb_save_path = "../model/keypoint_classifier.pkl"

@app.route('/predict', methods=['POST'])
def predict():
    model = XGBClassifier()
    model.load_model(xgb_save_path)
    if model:
        try:
            file = request.files['image']
            filestr = file.read()
            file_bytes = np.fromstring(filestr, np.uint8)
            image = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)
            image = cv.flip(image, 1)  # Mirror display
            # image = cv.rotate(image, cv.ROTATE_90_CLOCKWISE)

            # Detection implementation #############################################################
            debug_image = copy.deepcopy(image)

            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            image.flags.writeable = False

            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )

            # cv.imshow("image", image)
            # cv.waitKey(0)

            results = hands.process(image)
            image.flags.writeable = True

            #  ####################################################################
            if results.multi_hand_landmarks is not None:
                # print("[+] HAND DETECTED!")
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                    results.multi_handedness):
                    # Landmark calculation
                    pred_landmarks = calc_landmark_list(debug_image, hand_landmarks)
                    pred_landmarks = np.array(pred_landmarks)
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
