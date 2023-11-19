import os
import cv2 as cv
import time

images_dir = "G:/content/drive/MyDrive/augmented/train/images"
labels_dir = "G:/content/drive/MyDrive/augmented/train/labels"

image_names = sorted(os.listdir(images_dir))
label_names = sorted(os.listdir(labels_dir))


def convert_to_int(x):
    result = []
    for arr in x:
        result.append([float(y) for y in arr])
    return result


def show_brect(brect, img):
    dh, dw, _ = img.shape
    x, y, w, h = brect

    l = int((x - w / 2) * dw)
    r = int((x + w / 2) * dw)
    t = int((y - h / 2) * dh)
    b = int((y + h / 2) * dh)
    
    if l < 0:
        l = 0
    if r > dw - 1:
        r = dw - 1
    if t < 0:
        t = 0
    if b > dh - 1:
        b = dh - 1

    cv.rectangle(img, (l, t), (r, b), (0, 0, 255), 2)


for (image, label) in zip(image_names, label_names):
    image = cv.imread(os.path.join(images_dir, image))
    labels = open(os.path.join(labels_dir, label), "r").read().split('\n')
    brect_cords = [x.split(' ')[1::] for x in labels]
    
    brect_cords = convert_to_int(brect_cords)
    for rect in brect_cords:
        show_brect(rect, image)

    # brect = cv.rectangle(image, (x, y), (x2, y2), (0, 0, 255), 2)
    cv.imshow("test", image)
    cv.waitKey(10)
    time.sleep(0.5)


