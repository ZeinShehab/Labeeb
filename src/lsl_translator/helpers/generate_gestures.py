import time
import csv
import os
import cv2 as cv
import itertools
import imutils
import numpy as np
from lsl_translator.helpers import MediaPipe

NUM_CLASSES = 54

print(os.getcwd())

data_dir = 'D:/capstone-datasets/multi_hand_gestures/'
gesture_save_path = '../../../data/multi_hand_gestures.csv'

mp = MediaPipe()


def logging_csv(number, landmark_list):
    if 0 <= number <= NUM_CLASSES:
        csv_path = gesture_save_path
        # csv_path = 'data/train.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    return


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


def main():
    url = 'http://192.168.0.102:8080/video'
    cap_device = url
    cap_width = 500
    cap_height = 300

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    frames_per_gesture = 13
    frame_idx = 0
    gesture_index = 0
    gesture_data_path = os.path.join(data_dir, str(gesture_index))

    image_history = []

    if not os.path.exists(gesture_data_path):
        os.mkdir(gesture_data_path)


    print("[*] INFO: Beginning capture in 2 seconds...")
    time.sleep(2)
    while frame_idx < frames_per_gesture:
        key = cv.waitKey(10)

        if key == 27: # ESC
            break

        ret, image = cap.read()
        if not ret:
            continue

        # image = resize_image(image)
        landmark_list = mp.get_multi_hand_landmarks(image)


        if landmark_list is not None:
            image_history.append(image)
            save_image(gesture_data_path, image, gesture_index, frame_idx)
            frame_idx += 1
            print(f"[*] INFO: Chnage Frame!!!")
            time.sleep(0.1)

        cv.imshow('Hand Gesture Recognition', image)

    cap.release()
    cv.destroyAllWindows()

    landmark_list = mp.get_multi_hand_landmarks_gesture(image_history)
    logging_csv(gesture_index, landmark_list)

    # landmark_history == list(itertools.chain.from_iterable(landmark_history))


if __name__ == '__main__':
    main()