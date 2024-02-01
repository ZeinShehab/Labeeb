from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import joblib
import traceback
import cv2 as cv
import copy
import mediapipe as mp
from flask_restful import reqparse
import itertools
app = Flask(__name__)
import xgboost as xgb
from xgboost import XGBClassifier
import pickle
from generate_keypoints import calc_landmark_list

xgb_save_path = "../model/keypoint_classifier.pkl"

@app.route('/predict', methods=['POST'])
def predict():
    # model = pickle.load(open(xgb_save_path, "rb"))
    # model = joblib.load("../model/keypoint_classifier.pkl")
    model = XGBClassifier()
    model.load_model(xgb_save_path)
    if model:
        try:
            file = request.files['image']
            filestr = file.read()
            #convert string data to numpy array
            file_bytes = np.fromstring(filestr, np.uint8)
            # convert numpy array to image
            image = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)
            # print(type(file))
            # image = cv.imread(file)
            image = cv.flip(image, 1)  # Mirror display
            image = cv.rotate(image, cv.ROTATE_90_CLOCKWISE)
            # cv.imshow("App Image", image)
            # cv.waitKey(0)
            debug_image = copy.deepcopy(image)
            # Detection implementation #############################################################
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            image.flags.writeable = False

            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            results = hands.process(image)
            image.flags.writeable = True

            #  ####################################################################
            if results.multi_hand_landmarks is not None:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                    results.multi_handedness):
                    # Landmark calculation
                    pred_landmarks = calc_landmark_list(debug_image, hand_landmarks)
                    pred_landmarks = np.array(pred_landmarks)
                    pred_landmarks = pred_landmarks.reshape(1, -1)
                    pred = model.predict(pred_landmarks)

                    print(pred[0])
                return jsonify({'prediction': int(pred[0])})
            else:
                return jsonify({'prediction': -1})
        except:        
            return jsonify({'trace': traceback.format_exc(), 'prediction':-1})
    else:
        return ('No model here to use')
    

def calc_pred_landmarks(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        # landmark_x = min(int(landmark.x * image_width), image_width - 1)
        # landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_x = float(landmark.x)
        landmark_y = float(landmark.y)
        landmark_z = float(landmark.z)

        landmark_point.append([landmark_x, landmark_y, landmark_z])

    return landmark_point

if __name__ == '__main__':
    app.run(debug=True)
