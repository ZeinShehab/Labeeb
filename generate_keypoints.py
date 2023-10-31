#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import itertools

import os

import cv2 as cv
import mediapipe as mp

NUM_CLASSES = 32

images_dir = "D:/new-archive/datasets/valid/images"
data_save_path = "data/test.csv"

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

                landmark_list = list(itertools.chain.from_iterable(landmark_list))
                # Conversion to relative coordinates / normalized coordinates
                # pre_processed_landmark_list = pre_process_landmark(
                    # landmark_list)
                
                max_value = max(list(map(abs, landmark_list)))

                def normalize_(n):
                    return n / max_value

                landmark_list = list(map(normalize_, landmark_list))

                # print(landmark_list)

                # print(pre_processed_landmark_list)
                # Write to the dataset file
                # logging_csv(number, pre_processed_landmark_list)
                logging_csv(number, landmark_list)

                index += 1
                print(f"[+] Processed image {image_name}")
                iterations = 0

        iterations += 1
    print(f"Skipped {skipped} images!")


def calc_landmark_list(image, landmarks):
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


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


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
