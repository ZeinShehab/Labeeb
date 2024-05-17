import cv2 as cv

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from lsl_translator.utils import MediaPipe
from lsl_translator.utils import HandLandmarkerUtil

import itertools



image = cv.imread('C:/Users/zeins/LSL_Translator/src/lsl_translator/test/test_image1.jpg')

# model_path = "C:/Users/zeins/LSL_Translator/src/lsl_translator/model/hand_landmarker.task"

# BaseOptions = mp.tasks.BaseOptions
# HandLandmarker = vision.HandLandmarker
# HandLandmarkerOptions = vision.HandLandmarkerOptions
# VisionRunningMode = vision.RunningMode

# # Create a hand landmarker instance with the image mode:
# options = HandLandmarkerOptions(
#     base_options=BaseOptions(model_asset_path=model_path),
#     running_mode=VisionRunningMode.IMAGE,
#     num_hands=2)

# detector = HandLandmarker.create_from_options(options)
# result = detector.detect(mp_image)


# def pre_process_landmarks(image, landmarks):
#     image_width, image_height = image.shape[1], image.shape[0]
#     landmark_points = []

#     # Keypoint
#     for _, landmark in enumerate(landmarks):
#         landmark_x = float(min(float(landmark.x * image_width), image_width - 1))
#         landmark_y = float(min(float(landmark.y * image_height), image_height - 1))
#         landmark_z = float(landmark.z)      

#         landmark_points.append([landmark_x, landmark_y, landmark_z])

#     return landmark_points  


# def calc_relative_landmark_list(landmarks):
#     landmark_points = []
#     base_x, base_y, base_z = 0, 0, 0

#     index = 0
#     for landmark in landmarks:
#         landmark_x, landmark_y, landmark_z = landmark[0], landmark[1], landmark[2]

#         if index == 0:
#             base_x, base_y, base_z = landmark_x, landmark_y, landmark_z
        
#         landmark_x = landmark_x - base_x
#         landmark_y = landmark_y - base_y
#         landmark_z = landmark_z - base_z

#         landmark_points.append([landmark_x, landmark_y, landmark_z])
#         index += 1

#     landmark_points = list(itertools.chain.from_iterable(landmark_points))
#     max_value = max(list(map(abs, landmark_points)))

#     def normalize_(n):
#         return n / max_value

#     landmark_points = list(map(normalize_, landmark_points))

#     return landmark_points


# landmarks = result.hand_landmarks

# multi_hand_landmarks = []

# if result.hand_landmarks is not None:
#     for hand_landmarks in result.hand_landmarks:
#         pre_processed_landmarks = pre_process_landmarks(image, hand_landmarks)

#         print(pre_processed_landmarks)

#         hand_landmark_list = calc_relative_landmark_list(pre_processed_landmarks)
#         multi_hand_landmarks.append(hand_landmark_list)

#     if len(result.hand_landmarks) == 1:   
#         multi_hand_landmarks.append([0.0 for _ in range(63)])

#     multi_hand_landmarks = list(itertools.chain.from_iterable(multi_hand_landmarks))

# print(multi_hand_landmarks)
mp_image = mp.Image.create_from_file('C:/Users/zeins/LSL_Translator/src/lsl_translator/test/test_image2.jpg')

hand_landmarker = HandLandmarkerUtil()
multi_hand_landmarks = hand_landmarker.get_multi_hand_landmarks(mp_image)
print(multi_hand_landmarks)