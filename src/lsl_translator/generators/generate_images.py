import argparse
import os
import cv2 as cv
import copy
import itertools
import mediapipe as mp
import csv
import time
import imutils
import numpy as np
from lsl_translator.utils import MediaPipe

# images_dir = 'D:\Data\LSL_Word_Images_v2_Split/words_test'
train_dir = 'D:\Data\LSL_Word_Images_v2_Split/words_train'
test_dir = 'D:\Data\LSL_Word_Images_v2_Split/words_test'
csv_path_train = 'data/multi_hand_word_train.csv'
csv_path_test  = 'data/multi_hand_word_test.csv'

mp = MediaPipe()

def logging_csv(number, landmark_list, csv_path):
    with open(csv_path, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *landmark_list])

# def save_image(image, image_number, image_idx):
#     image_filename = os.path.join(images_dir, f'{image_number}_{image_idx}.jpg')
    
#     resized_image = imutils.resize(image, width=400, height=400)
    
#     canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
#     # recenter image
#     y_offset = (400 - resized_image.shape[0]) // 2
#     x_offset = (400 - resized_image.shape[1]) // 2
    
#     # add white border
#     canvas[y_offset:y_offset + resized_image.shape[0], x_offset:x_offset + resized_image.shape[1]] = resized_image
    
#     compression_params = [cv.IMWRITE_JPEG_QUALITY, 80]
#     cv.imwrite(image_filename, canvas, compression_params)
    
#     print(f"[+] Saved image: {image_number}_{image_idx}")

def resize_image(image):
    resized_image = imutils.resize(image, width=400, height=400)
    
    canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    y_offset = (400 - resized_image.shape[0]) // 2
    x_offset = (400 - resized_image.shape[1]) // 2
    
    canvas[y_offset:y_offset + resized_image.shape[0], x_offset:x_offset + resized_image.shape[1]] = resized_image
    
    return canvas

def save_image(images_dir, resized_image, image_number, image_idx):
    image_filename = os.path.join(images_dir, f'{image_number}_{image_idx}.jpg')
    
    compression_params = [cv.IMWRITE_JPEG_QUALITY, 80]
    cv.imwrite(image_filename, resized_image, compression_params)
    
    print(f"[+] Saved image: {image_number}_{image_idx}")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    args = parser.parse_args()

    return args

def multihanded(landmark_list):
    second_half = [lm for lm in landmark_list[63:]]

    if all([v == 0.0 for v in second_half]):
        return 1
    else: 
        return 2

def main():
    args = get_args()
    
    nb_of_hands = 1

    cap_device = 0
    cap_width = args.width
    cap_height = args.height

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    time.sleep(0.5)

    idx =   720      
    number = 49                          # Number of word in labels

    iterations = 840                     # Entries per Word
    print("Prepare to start capture")
    time.sleep(2)
    while True and idx < iterations:
        time.sleep(0.15)
        # time.sleep(0.75)
        key = cv.waitKey(10)

        if key == 27:
            break

        _, image = cap.read()
        image = resize_image(image)
        landmark_list = mp.get_multi_hand_landmarks(image)
    
        if landmark_list is not None and multihanded(landmark_list) == nb_of_hands:

                logging_csv(number, landmark_list,csv_path_test)
                save_image(test_dir, image, number, idx)
                idx += 1

        cv.imshow('Hand Gesture Recognition', image)

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
