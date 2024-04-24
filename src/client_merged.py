import cv2 as cv 
import time
import requests
import os
from lsl_translator.utils import MediaPipe
from argparse import ArgumentParser
from lsl_translator.generators import GeneratorUtils

mp = MediaPipe()
gu = GeneratorUtils()

def capture_frame():
    cap_device = 0
    cap_width = 960
    cap_height = 540

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    _, image = cap.read()
    cap.release()

    return image

def save_image(frame, filename):
    cv.imwrite(filename, frame)

def make_request_static(frame, server_url):
    temp_filename = "temp_image.jpg"
    save_image(frame, temp_filename)

    files = {'image': open(temp_filename, 'rb')}
    response = requests.post(server_url, files=files)
    files['image'].close()

    if response.status_code == 200:
        result = response.json()
        print("Static Image Prediction:", result)
    else:
        print("Error:", response.status_code, response.text)

    os.remove(temp_filename)

def make_request_gesture(frames, server_url):
    files = [('image', open(temp_filename, 'rb')) for temp_filename in frames]

    response = requests.post(server_url, files=files)

    if response.status_code == 200:
        result = response.json()
        print("Gesture Prediction:", result)
    else:
        print("Error:", response.status_code, response.text)

def main():

    server_url = "http://127.0.0.1:5000"
    server_url_static = server_url + "/predict"
    server_url_gesture = server_url + "/predict_gesture"

    gesture_response, symbol_response = 0, 0

    names = []

    idx = 0
    while idx < 10:
        frame = capture_frame()
        cv.imshow("Video Input", frame)
        cv.waitKey(10)

        if idx == 0: 
            symbol_response = make_request_static(frame, server_url_static)

        landmark_list = mp.get_multi_hand_landmarks(frame)
        if landmark_list is not None:
            name = f'image_{idx}.jpg'
            save_image(frame, name)
            names.append(name)
            idx += 1 
    
    gesture_response = make_request_gesture(names, server_url_gesture)

    print("Gesture Output: ", gesture_response)
    print("Symbol  Output: ", symbol_response)

    cv.destroyAllWindows()

    

if __name__ == '__main__':
    main()
