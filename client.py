import requests
import cv2
import base64
import os
import argparse
import copy
import time

def capture_frame():
    args = get_args()

    url = 'http://192.168.229.173:8080/video'
    cap_device = url
    cap_width = args.width
    cap_height = args.height

    cap = cv2.VideoCapture(cap_device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)

    _, image = cap.read()
    cap.release()

    debug_image = copy.deepcopy(image)

    return debug_image

def save_image(frame, filename):
    cv2.imwrite(filename, frame)

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    args = parser.parse_args()

    return args

def make_request(frame, server_url):
    # Save the image temporarily
    temp_filename = "temp_image.jpg"
    save_image(frame, temp_filename)

    # Prepare data as form request
    files = {'image': open(temp_filename, 'rb')}

    response = requests.post(server_url, files=files)

    # Close the file before attempting to remove it
    files['image'].close()

    if response.status_code == 200:
        result = response.json()
        print("Server response:", result)
    else:
        print("Error:", response.status_code, response.text)

    # Remove the temporary image file
    os.remove(temp_filename)

if __name__ == "__main__":
    server_url = "http://127.0.0.1:5000/predict"

    while True:
        frame = capture_frame()

        cv2.imshow("Video Input", frame)
        
        make_request(frame, server_url)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):  # press q to quit
            break

    cv2.destroyAllWindows()