from lsl_translator.utils import MediaPipe
import cv2 as cv
import os
import numpy as np
import requests
import http
from lsl_translator.generators import GeneratorUtils
import copy
import time
from xgboost import XGBClassifier
model_save_path = 'C:/Users/zeinshehab/LSL_Translator/src/lsl_translator/model/gesture_classifier.pkl'
model2_save_path = 'C:/Users/zeinshehab/LSL_Translator/src/lsl_translator/model/symbol_classifier.pkl'

image = cv.imread('C:/Users/zeinshehab/LSL_Translator/test/test_image2.jpg')

gu = GeneratorUtils()
mp = MediaPipe()
path = "C:/Users/zeinshehab/LSL_Translator/images/temp/0"
data = os.listdir(path)

# print(data)

images = []
for name in data:
    images.append(cv.imread(os.path.join(path, name)))

# cv.imshow("image", im1)
# cv.waitKey(0)
server_url = "http://127.0.0.1:5000/predict_gesture"

def save_image(frame, filename):
    cv.imwrite(filename, frame)

for image in images:
    print(mp.contains_landmarks(image))
 
frame_index = 0
names = []
for frame in images:
    name = f'temp_image{frame_index}.jpg'
    save_image(frame, name)
    frame_index += 1
    names.append(name)

# Prepare data as form request
# files = [open(temp_filename, 'rb') for temp_filename in names]
# files = {'image': files}
files = [('image', open(temp_filename, 'rb')) for temp_filename in names]
# print(files)
# files = {'images' : files}

response = requests.post(server_url, files=files)

# Close the file before attempting to remove it
# files['image'].close()

for file in files:
    file[1].close()

if response.status_code == 200:
    result = response.json()
    print("Server response:", result)
else:
    print("Error:", response.status_code, response.text)

# Remove the temporary image file
    # os.remove(temp_filename)

# symbol_landmarks = mp.get_multi_hand_landmarks(image)
# gesture_landmarks = mp.get_multi_hand_landmarks_gesture(images)
# # # print(gesture_landmarks)

# loaded_model = XGBClassifier()
# loaded_model.load_model(model_save_path)

# # xs = np.array(symbol_landmarks)
# xs = np.array(gesture_landmarks)
# xs = xs.reshape((1, -1))


# prediction = loaded_model.predict(xs)
# p = loaded_model.predict_proba(xs)
# print(prediction)
# print(p)

# xs1 = list(range(1, 10, 3))
# xs2 = list(range(2, 10, 3))
# xs3 = list(range(3, 10, 3))
# print(xs1)
# print(xs2)
# print(xs3)

# xs = [[0.0, 0.0] for x in range(5)]
# print(xs) 
# xs[0][0] = 1.0
# print(xs)



# import numpy as np

# data_directory = "data/"
# train_dataset = f'{data_directory}gesture_train.csv'
# test_dataset = f'{data_directory}gesture_test.csv'
# augmented_dataset = f'{data_directory}augmented_gestures_test.csv'

# recorded_gesture = np.loadtxt(train_dataset, delimiter=',', dtype='float32', usecols=list(range(1, (126 * 10) + 1)))
# augmented_gesture = np.loadtxt(augmented_dataset, delimiter=',', dtype='float32', usecols=list(range(1, (126 * 10) + 1)))

# print(len(recorded_gesture[0]))
# print(len(augmented_gesture[0]))

# mapped_recorded = list(map(abs, recorded_gesture[0]))
# mapped_augmented = list(map(abs, augmented_gesture[0]))

# difference = np.subtract(mapped_augmented, mapped_recorded)
# difference = list(map(abs, difference))
# print(np.average(difference))


def capture_frames(count=10):
    
    cap_device = 0
    cap_width = 960
    cap_height = 540

    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
    
    frames = []
    
    for _ in range(count):
        _, image = cap.read()
        debug_image = copy.deepcopy(image)
        frames.append(debug_image)
        time.sleep(0.5)

    cap.release()
    return frames

def save_frames(frames):
    temp_files = []
    for i, frame in enumerate(frames):
        temp_filename = f"temp_image_{i}.jpg"
        cv.imwrite(temp_filename, frame)
        temp_files.append(temp_filename)
    return temp_files


def make_request(temp_files, server_url):
    files = {f"image_{i}": open(file, 'rb') for i, file in enumerate(temp_files)}

    response = requests.post(server_url, files=files)

    for f in files.values():
        f.close()

    if response.status_code == 200:
        result = response.json()
        print("Server response:", result)
    else:
        print("Error:", response.status_code, response.text)

    for file in temp_files:
        os.remove(file)

if __name__ == "__main__":
    server_url = "http://127.0.0.1:5000/predict_gesture"
    
    while True:
        frames = capture_frames(count=10)
        
        temp_files = save_frames(frames)         
        
        make_request(temp_files, server_url)
        
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cv.destroyAllWindows()