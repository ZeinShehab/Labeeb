import cv2 as cv
import time
from lsl_translator.utils import MediaPipe
from lsl_translator.generators import GeneratorUtils

train_dir = 'D:\Data\LSL_Word_Images_v2_Split/words_train'
test_dir = 'D:\Data\LSL_Word_Images_v2_Split/words_test'
csv_path_train = 'data/multi_hand_word_train.csv'
csv_path_test  = 'data/multi_hand_word_test.csv'

mp = MediaPipe()
gu = GeneratorUtils()

def main():
    nb_of_hands = 1

    cap_device = 0
    cap_width = 960
    cap_height = 540

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    time.sleep(0.5)

    idx         =   720
    number      = 57
    iterations  = 840

    training    = False if (idx == 300 or idx == 720) else True

    log_path    = csv_path_train if training else csv_path_test 
    save_path   = train_dir if training else test_dir

    print("Prepare to start capture")
    time.sleep(2)
    while True and idx < iterations:
        # time.sleep(0.15)
        time.sleep(0.5)
        key = cv.waitKey(10)

        if key == 27:
            break

        _, image = cap.read()

        image = gu.resize_image(image)
        landmark_list = mp.get_multi_hand_landmarks(image)
    
        if landmark_list is not None and mp.num_hands(landmark_list) == nb_of_hands:

            gu.log_to_csv(number, landmark_list, log_path)
            gu.save_image(save_path, image, number, idx)
            idx += 1

        cv.imshow('Hand Gesture Recognition', image)

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
