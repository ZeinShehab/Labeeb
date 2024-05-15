#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from lsl_translator.utils import HandLandmarkerUtil
from lsl_translator.generators import GeneratorUtils

images_dir = "D:/capstone-datasets/new-archive/datasets/valid/images"
data_save_path = "data/alphabet_task_test.csv"
hand_landmarker = HandLandmarkerUtil()
gu = GeneratorUtils()

def main():
    images = sorted(os.listdir(images_dir), key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1].split('.')[0])))
    index = 0
    max_iter = 3
    iterations = 0
    skipped = 0

    while True and index < len(images):
        image_name = images[index]
        number = int(image_name.split('_')[0])
        image_path = f"{images_dir}/{image_name}"

        if iterations >= max_iter:
            print(f"[-] Skipping image {image_name}")
            index += 1
            skipped += 1
            iterations = 0
        
        mp_image = HandLandmarkerUtil.mp_image_from_path(image_path)
        landmark_list = hand_landmarker.get_multi_hand_landmarks(mp_image)

        if len(landmark_list) != 0:
                gu.log_to_csv(number, landmark_list, data_save_path)
                index += 1
                print(f"[+] Processed image {image_name}")
                iterations = 0

        iterations += 1
    print(f"Skipped {skipped} images!")


if __name__ == '__main__':
    main()
