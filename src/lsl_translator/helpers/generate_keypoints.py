#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import cv2 as cv
from mediapipe_helper import MediaPipe

NUM_CLASSES = 32

images_dir = "D:/capstone-datasets/new-archive/datasets/valid/images"
data_save_path = "data/multi_hand_alph_test.csv"
mp = MediaPipe()

def main():
    images = os.listdir(images_dir)
    index = 0
    max_iter = 3
    iterations = 0
    skipped = 0

    while True and index < len(images):

        image_name = images[index]
        number = int(image_name.split('_')[0])

        image = cv.imread(f"{images_dir}/{image_name}")

        if iterations >= max_iter:
            print(f"[-] Skipping image {image_name}")
            index += 1
            skipped += 1
            iterations = 0
            
        landmark_list = mp.get_multi_hand_landmarks(image)

        if landmark_list is not None:
                logging_csv(number, landmark_list)
                index += 1
                print(f"[+] Processed image {image_name}")
                iterations = 0

        iterations += 1
    print(f"Skipped {skipped} images!")


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
