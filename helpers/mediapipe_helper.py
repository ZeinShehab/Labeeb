import csv
import copy
import itertools

import cv2 as cv
import mediapipe as mp


class MediaPipe:
    USE_STATIC_IMAGE_MODE = True
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.5

    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode = self.USE_STATIC_IMAGE_MODE,
            min_detection_confidence = self.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence  = self.MIN_TRACKING_CONFIDENCE,
            max_num_hands = 2,
        )


    def get_multi_hand_landmarks(self, image):
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True

        multi_hand_landmarks = []

        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_landmark_list = self.calc_landmark_list(debug_image, hand_landmarks)
                multi_hand_landmarks.append(hand_landmark_list)

            # if one handed image pad with zeros on either left or right
            if len(results.multi_hand_landmarks) == 1:
                # 0=left 1=right
                handedness = results.multi_handedness[0].classification[0].index
                multi_hand_landmarks.insert(1-handedness, [0.0 for _ in range(63)])

            multi_hand_landmarks = list(itertools.chain.from_iterable(multi_hand_landmarks))
            return multi_hand_landmarks

        return None

    def calc_landmark_list(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_points = []
        base_x, base_y, base_z = 0, 0, 0

        # Keypoint
        for index, landmark in enumerate(landmarks.landmark):
            landmark_x = float(min(float(landmark.x * image_width), image_width - 1))
            landmark_y = float(min(float(landmark.y * image_height), image_height - 1))
            landmark_z = float(landmark.z)

            if index == 0:
                base_x, base_y, base_z = landmark_x, landmark_y, landmark_z
            
            landmark_x = landmark_x - base_x
            landmark_y = landmark_y - base_y
            landmark_z = landmark_z - base_z

            landmark_points.append([landmark_x, landmark_y, landmark_z])

        landmark_points = list(itertools.chain.from_iterable(landmark_points))
                
        max_value = max(list(map(abs, landmark_points)))

        def normalize_(n):
            return n / max_value

        landmark_points = list(map(normalize_, landmark_points))
        return landmark_points