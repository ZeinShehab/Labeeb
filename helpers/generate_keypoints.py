#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import itertools

import os

import cv2 as cv
import mediapipe as mp

NUM_CLASSES = 32

images_dir = "D:/capstone-datasets/new-archive/datasets/valid/images"
data_save_path = "../data/alphabet_test.csv"


def main():
    use_static_image_mode = True
    min_detection_confidence = 0.5
    min_tracking_confidence = 0.5

    # Model load #############################################################
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=2,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    images = os.listdir(images_dir)
    index = 0
    max_iter = 3
    iterations = 0
    skipped = 0

    while True and index < len(images):

        image_name = images[index]
        number = int(image_name.split('_')[0])

        image = cv.imread(f"{images_dir}/{image_name}")
        # image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        # Detection implementation #############################################################
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        if iterations >= max_iter:
            print(f"[-] Skipping image {image_name}")
            index += 1
            skipped += 1
            iterations = 0
            

        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                # Write to the dataset file
                logging_csv(number, landmark_list)

                index += 1
                print(f"[+] Processed image {image_name}")
                iterations = 0

        iterations += 1
    print(f"Skipped {skipped} images!")


def calc_landmark_list(image, landmarks):
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


def logging_csv(number, landmark_list):
    if 0 <= number <= NUM_CLASSES:
        csv_path = data_save_path
        # csv_path = 'data/train.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    return


if __name__ == '__main__':
    main()
