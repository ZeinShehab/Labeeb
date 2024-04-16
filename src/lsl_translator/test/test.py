from lsl_translator.helpers.mediapipe_helper import MediaPipe
import cv2 as cv
import os

mp = MediaPipe()
path = "D:/capstone-datasets/multi_hand_gestures/test/"
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
print(gesture_landmarks)