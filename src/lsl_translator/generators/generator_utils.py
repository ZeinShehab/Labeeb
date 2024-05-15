import imutils
import numpy as np
import csv
import cv2 as cv
import os


class GeneratorUtils:
    NUM_CLASSES = 58

    def __init__(self) -> None:
        pass


    def resize_image(self, image):
        resized_image = imutils.resize(image, width=400, height=400)
        
        canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
        
        y_offset = (400 - resized_image.shape[0]) // 2
        x_offset = (400 - resized_image.shape[1]) // 2
        
        canvas[y_offset:y_offset + resized_image.shape[0], x_offset:x_offset + resized_image.shape[1]] = resized_image
        
        return canvas

    def save_image(self, images_dir, resized_image, gesture_index, sequence_number, frame_idx):
        image_filename = os.path.join(images_dir, f'{gesture_index}_{sequence_number}_{frame_idx}.jpg')
        
        compression_params = [cv.IMWRITE_JPEG_QUALITY, 80]
        cv.imwrite(image_filename, resized_image, compression_params)
        
        print(f"[+] Saved image: {sequence_number}_{frame_idx}")


    def log_to_csv(self, class_index, landmark_list, csv_path):
        if 0 <= class_index <= self.NUM_CLASSES:
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([class_index, *landmark_list])
            return