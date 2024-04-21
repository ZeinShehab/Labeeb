from lsl_translator.utils import MediaPipe
import cv2 as cv
import os
import numpy as np

from xgboost import XGBClassifier
model_save_path = 'C:/Users/zeins/LSL_Translator/src/lsl_translator/model/gesture_classifier.pkl'
model2_save_path = 'C:/Users/zeins/LSL_Translator/src/lsl_translator/model/keypoint_classifier.pkl'

image = cv.imread('C:/Users/zeins/LSL_Translator/src/lsl_translator/test/test_image2.jpg')


mp = MediaPipe()
path = "C:/Users/zeins/LSL_Translator/images/temp/0"
data = os.listdir(path)

print(data)

images = []
for name in data:
    images.append(cv.imread(os.path.join(path, name)))

# cv.imshow("image", im1)
# cv.waitKey(0)

for image in images:
    print(mp.contains_landmarks(image))

symbol_landmarks = mp.get_multi_hand_landmarks(image)
gesture_landmarks = mp.get_multi_hand_landmarks_gesture(images)
# # print(gesture_landmarks)

loaded_model = XGBClassifier()
loaded_model.load_model(model_save_path)

# xs = np.array(symbol_landmarks)
xs = np.array(gesture_landmarks)
xs = xs.reshape((1, -1))


prediction = loaded_model.predict(xs)
p = loaded_model.predict_proba(xs)
print(prediction)
print(p)

# xs1 = list(range(1, 10, 3))
# xs2 = list(range(2, 10, 3))
# xs3 = list(range(3, 10, 3))
# print(xs1)
# print(xs2)
# print(xs3)

# xs = [[0.0, 0.0] for x in range(5)]
# print(xs) 
# xs[0][0] = 1.0
# print(xs)



# import numpy as np

# data_directory = "data/"
# train_dataset = f'{data_directory}gesture_train.csv'
# test_dataset = f'{data_directory}gesture_test.csv'
# augmented_dataset = f'{data_directory}augmented_gestures_test.csv'

# recorded_gesture = np.loadtxt(train_dataset, delimiter=',', dtype='float32', usecols=list(range(1, (126 * 10) + 1)))
# augmented_gesture = np.loadtxt(augmented_dataset, delimiter=',', dtype='float32', usecols=list(range(1, (126 * 10) + 1)))

# print(len(recorded_gesture[0]))
# print(len(augmented_gesture[0]))

# mapped_recorded = list(map(abs, recorded_gesture[0]))
# mapped_augmented = list(map(abs, augmented_gesture[0]))

# difference = np.subtract(mapped_augmented, mapped_recorded)
# difference = list(map(abs, difference))
# print(np.average(difference))
