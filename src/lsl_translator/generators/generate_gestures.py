import time
import os
import cv2 as cv
from lsl_translator.utils import MediaPipe
from lsl_translator.generators import GeneratorUtils

NUM_CLASSES = 54

data_dir = 'd:\Data\multi_hand_gestures'
gesture_save_path = 'data/gesture_test.csv'

mp = MediaPipe()
gu = GeneratorUtils()

def main():
    cap_device = 0
    cap_width = 960
    cap_height = 540

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    print("[*] Camera Ready")

    frames_per_gesture  = 10
    frame_idx           = 0
    gesture_index       = 1                                               
    sequence_nb         = 5
    image_history       = []
    
    gesture_data_path   = os.path.join(data_dir, f'{gesture_index}/test')

    if not os.path.exists(gesture_data_path):
        os.mkdir(gesture_data_path)


    print("[*] INFO: Beginning capture in 2 seconds...")
    time.sleep(1)
    print("1 Second Remaining...")
    time.sleep(1)
    print("Begin")

    while frame_idx < frames_per_gesture:
        key = cv.waitKey(10)

        if key == 27: # ESC
            break

        ret, image = cap.read()
        image = gu.resize_image(image)
        if not ret:
            continue

        if mp.contains_landmarks(image):

            image_history.append(image)
            gu.save_image(gesture_data_path, image, gesture_index, sequence_nb, frame_idx)
            frame_idx += 1
            time.sleep(0.15)

        cv.imshow('Hand Gesture Training', image)

    cap.release()
    cv.destroyAllWindows()

    landmark_list = mp.get_multi_hand_landmarks_gesture(image_history)
    mp.log_to_csv(gesture_index, landmark_list, gesture_save_path)
    print("Logged Keypoints")

if __name__ == '__main__':
    main()