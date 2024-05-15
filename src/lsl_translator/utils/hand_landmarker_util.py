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
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
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
    
    def pre_process_landmarks(self, mp_image, landmarks):
        image_width, image_height = mp_image.width, mp_image.height
        landmark_points = []

        # Keypoint
        for landmark in landmarks:
            landmark_x = float(min(float(landmark.x * image_width), image_width - 1))
            landmark_y = float(min(float(landmark.y * image_height), image_height - 1))
            landmark_z = float(landmark.z)      

            landmark_points.append([landmark_x, landmark_y, landmark_z])

        return landmark_points  

    def calc_relative_landmark_list(self, landmarks):
        landmark_points = []
        base_x, base_y, base_z = 0, 0, 0

        index = 0
        for landmark in landmarks:
            landmark_x, landmark_y, landmark_z = landmark[0], landmark[1], landmark[2]

            if index == 0:
                base_x, base_y, base_z = landmark_x, landmark_y, landmark_z
            
            landmark_x = landmark_x - base_x
            landmark_y = landmark_y - base_y
            landmark_z = landmark_z - base_z

            landmark_points.append([landmark_x, landmark_y, landmark_z])
            index += 1

        landmark_points = list(itertools.chain.from_iterable(landmark_points))
        max_value = max(list(map(abs, landmark_points)))

        def normalize_(n):
            return n / max_value

        landmark_points = list(map(normalize_, landmark_points))

        return landmark_points

    def get_multi_hand_landmarks(self, mp_image):
        results = self.detector.detect(mp_image)
        
        multi_hand_landmarks = []

        for hand_landmark_list in results.hand_landmarks:
            pre_processed_landmarks = self.pre_process_landmarks(mp_image, hand_landmark_list)
            relative_landmarks = self.calc_relative_landmark_list(pre_processed_landmarks)
            # for landmark in hand_landmark_list:
                # landmark_list.append([landmark.x, landmark.y, landmark.z])
            
            # landmark_list = list(itertools.chain.from_iterable(relative_landmarks))
            multi_hand_landmarks.append(relative_landmarks)

        if len(results.hand_landmarks) == 1:
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
        
def get_multi_hand_gesture_landmarks_video(self, mp_images):
    BaseOptions = mp.tasks.BaseOptions
    video_options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=self.model_path),
        running_mode=RunningMode.VIDEO,
        num_hands=2,
        # min_hand_detection_confidence=0.5,
        # min_tracking_confidence=0.5,
    )
    self.video_detector = HandLandmarker.create_from_options(video_options)

    time_stamp = 0
    time_stamp_difference = 10
    multi_hand_gesture_landmarks = []

    for mp_image in mp_images:

        results = self.video_detector.detect_for_video(mp_image, time_stamp)
        multi_hand_landmarks = []

        for hand_landmark_list in results.hand_landmarks:
            for landmark in hand_landmark_list: 
                multi_hand_landmarks.append([landmark.x, landmark.y, landmark.z])

        multi_hand_landmarks = list(itertools.chain.from_iterable(multi_hand_landmarks))
        multi_hand_gesture_landmarks.append(multi_hand_landmarks)
        time_stamp += time_stamp_difference

    multi_hand_gesture_landmarks = list(itertools.chain.from_iterable(multi_hand_gesture_landmarks))
    return multi_hand_gesture_landmarks