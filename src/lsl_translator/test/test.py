from lsl_translator.helpers.mediapipe_helper import MediaPipe
import cv2 as cv
import os
import numpy as np

from xgboost import XGBClassifier
model_save_path = 'C:/Users/zeinshehab/LSL_Translator/src/lsl_translator/model/gesture_classifier.pkl'

mp = MediaPipe()
path = "C:/Users/zeinshehab/LSL_Translator/images/temp/1"
data = os.listdir(path)

print(data)

images = []
for name in data:
    images.append(cv.imread(os.path.join(path, name)))

# cv.imshow("image", im1)
# cv.waitKey(0)

for image in images:
    print(mp.contains_landmarks(image))

gesture_landmarks = mp.get_multi_hand_landmarks_gesture(images)
# print(gesture_landmarks)

loaded_model = XGBClassifier()
loaded_model.load_model(model_save_path)

xs = np.array(gesture_landmarks)
xs = xs.reshape((1, -1))


prediction = loaded_model.predict(xs)
p = loaded_model.predict_proba(xs)
print(prediction)
print(p)