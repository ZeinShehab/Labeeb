import itertools
import mediapipe as mp
import itertools
import numpy as np

from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode


class HandLandmarkerUtil:
    def __init__(self) -> None:
        model_path = "C:/Users/zeins/LSL_Translator/src/lsl_translator/model/hand_landmarker.task"
        BaseOptions = mp.tasks.BaseOptions
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.IMAGE,
            num_hands=2,
            # min_detection_confidence=0.5,
            # min_tracking_confidence=0.5,
        )
        self.detector = HandLandmarker.create_from_options(options)

    def mp_image_from_path(image_path):
        return mp.Image.create_from_file(image_path)

    def mp_image_from_numpy(numpy_image):
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)

    def num_hands(landmark_list):
        second_half = [lm for lm in landmark_list[63:]]

        if all([v == 0.0 for v in second_half]):
            return 1
        else: 
            return 2

    def contains_landmarks(self, mp_image):
        results = self.detector.detect(mp_image)
        return len(results.hand_landmarks) != 0
    
    def get_multi_hand_landmarks(self, mp_image):
        results = self.detector.detect(mp_image)
        
        multi_hand_landmarks = []

        for hand_landmark_list in results.hand_landmarks:
            landmark_list = []
            for landmark in hand_landmark_list:
                landmark_list.append([landmark.x, landmark.y, landmark.z])
            
            landmark_list = list(itertools.chain.from_iterable(landmark_list))
            multi_hand_landmarks.append(landmark_list)

        if len(results.hand_landmarks) <= 1:
            multi_hand_landmarks.append([0.0 for _ in range(63)])
        
        multi_hand_landmarks = list(itertools.chain.from_iterable(multi_hand_landmarks))

        return multi_hand_landmarks

    def get_multi_hand_gesture_landmarks(self, mp_images):
        multi_hand_gesture_landmarks = []
        previous_frame_landmarks = []

        for mp_image in mp_images:
            current_frame_landmarks = self.get_multi_hand_landmarks(mp_image)

            if len(multi_hand_gesture_landmarks) >= 1:
                movement = np.subtract(current_frame_landmarks, previous_frame_landmarks)
                current_frame_landmarks = np.add(current_frame_landmarks, movement)

            previous_frame_landmarks = current_frame_landmarks
            multi_hand_gesture_landmarks.append(current_frame_landmarks)

        multi_hand_gesture_landmarks = list(itertools.chain.from_iterable(multi_hand_gesture_landmarks))
        return multi_hand_gesture_landmarks
        
                