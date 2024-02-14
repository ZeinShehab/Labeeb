import argparse
import os
import cv2 as cv
import copy
import itertools
import mediapipe as mp
import csv
import time
from generate_keypoints import calc_landmark_list
use_static_image_mode = True
min_detection_confidence = 0.5
min_tracking_confidence = 0.5
images_dir = '/Users/raedfidawi/LSL_Word_Images'
csv_path_train = '../data/word_keypoints_train.csv'
csv_path_test  = '../data/word_keypoints_test.csv'
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=2,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)


def logging_csv(number, landmark_list, csv_path):
    with open(csv_path, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *landmark_list])

def save_image(image, image_number, image_idx):
    image_filename = os.path.join(images_dir, f'{image_number}_{image_idx}.png')
    cv.imwrite(image_filename, image)
    print(f"[+] Saved image: {image_number}_{image_idx}")

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    args = parser.parse_args()

    return args

def main():
    global use_static_image_mode
    global min_detection_confidence
    global min_tracking_confidence

    args = get_args()

    cap_device = 1
    cap_width = args.width
    cap_height = args.height

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    time.sleep(0.5)

    idx = 0         
    number = 35                          # Number of word in labels

    iterations = 420                     # Entries per Word
    print("Prepare to start capture")
    time.sleep(2)
    while True and idx < iterations:
        time.sleep(0.15)
        key = cv.waitKey(10)

        if key == 27:
            break

        _, image = cap.read()

        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                if idx <= 300:
                    logging_csv(number, landmark_list,csv_path_train)
                else:
                    logging_csv(number, landmark_list,csv_path_test)

            save_image(image, number, idx)
            idx += 1
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
