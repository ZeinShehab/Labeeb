import time
import os
import cv2 as cv
from lsl_translator.utils import MediaPipe
from lsl_translator.generators import GeneratorUtils

NUM_CLASSES                 = 54
gesture_index               = 2
FRAMES_PER_GESTURE          = 10

data_dir                    = 'd:/Data/multi_hand_gestures'
gesture_save_path_train     = 'data/gesture_train.csv'
gesture_save_path_test      = 'data/gesture_test.csv'

gesture_data_path_train     = os.path.join(data_dir, f'{gesture_index}/train')
gesture_data_path_test      = os.path.join(data_dir,  f'{gesture_index}/test')

mp = MediaPipe()
gu = GeneratorUtils()

def create_directory(base_path, class_number):
        directory_name = f"{class_number}"
        directory_path = os.path.join(base_path, directory_name)
        os.makedirs(directory_path)
        os.makedirs(os.path.join(directory_path, "train"))
        os.makedirs(os.path.join(directory_path, "test"))

def main():
    frame_idx  = 0
    cap_device = 0
    cap_width  = 960
    cap_height = 540

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    print("[*] Camera Ready")

    sequence_nb  = 5
    
    gesture_data_path = gesture_data_path_test
    gesture_save_path = gesture_save_path_test

    if not os.path.exists(gesture_data_path):
        create_directory(data_dir, gesture_index)
    
    f"""
        Do not change {FRAMES_PER_GESTURE}, {frame_idx}

        Change {sequence_nb} per run

        Change {gesture_index} for each class

        Change {gesture_data_path}, {gesture_save_path} based on training or testing
    """

    print("Data Path", gesture_data_path, "\n\n Save path: ", gesture_save_path)

    print("[*] INFO: Beginning capture in 2 seconds...")

    for i in range(0, 2):
        print(f"{2-i} Seconds Remaining...")
        time.sleep(1)

    image_history       = []

    while frame_idx < FRAMES_PER_GESTURE:
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
    gu.log_to_csv(gesture_index, landmark_list, gesture_save_path)
    print("Logged Keypoints")
    print(f"[!] NOTE: CHANGE SEQUENCE NUMBER to {sequence_nb + 1}!")
    print("[!] NOTE: CHANGE GESTURE INDEX IF STARTING NEW GESTURE!")

if __name__ == '__main__':
    main()