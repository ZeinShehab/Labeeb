import time
import csv
import os
import cv2 as cv
import itertools
import imutils
import numpy as np
from lsl_translator.utils import MediaPipe

NUM_CLASSES = 54
gesture_index = 0 
# print(os.getcwd())

data_dir = 'd:\Data\multi_hand_gestures'
gesture_save_path = 'data/gesture_test.csv'

mp = MediaPipe()


def logging_csv(number, landmark_list):
    
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


def save_image(images_dir, resized_image, image_number, sequence_nb, image_idx):
    image_filename = os.path.join(images_dir, f'{image_number}__{sequence_nb}_{image_idx}.jpg')
    
    compression_params = [cv.IMWRITE_JPEG_QUALITY, 80]
    cv.imwrite(image_filename, resized_image, compression_params)
    
    print(f"[+] Saved image: {image_number}_{sequence_nb}_{image_idx}")


def main():

    cap_device = 0
    cap_width = 960     #500
    cap_height = 540    #300

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
    print("[*] Camera Ready")
    frames_per_gesture = 10
    frame_idx = 0                                                   # automatically updated
    gesture_index = 1                                               # Update per class
    sequence_nb = 5                                                 # Update per run
    gesture_data_path = os.path.join(data_dir, f'{gesture_index}/test')
    print(gesture_data_path)
    image_history = []

    # if not os.path.exists(gesture_data_path):
    #     os.mkdir(gesture_data_path)


    print("[*] INFO: Beginning capture in 2 seconds...")
    time.sleep(1)
    print("######## 1 #######")
    time.sleep(1)
    print("GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

    ### maybe need to classify symbol first per frame then save to avoid missclassification
    while frame_idx < frames_per_gesture:
        key = cv.waitKey(10)

        if key == 27: # ESC
            break

        ret, image = cap.read()
        image = resize_image(image)
        if not ret:
            continue

        # image = resize_image(image)

        if mp.contains_landmarks(image):
            image_history.append(image)
            save_image(gesture_data_path, image, gesture_index, sequence_nb, frame_idx)
            frame_idx += 1
            # print(f"[*] INFO: Change Frame!!!")
            time.sleep(0.15)

        cv.imshow('Hand Gesture Training', image)

    cap.release()
    cv.destroyAllWindows()

    landmark_list = mp.get_multi_hand_landmarks_gesture(image_history)
    logging_csv(gesture_index, landmark_list)
    print("Logged Keypoints")

if __name__ == '__main__':
    main()