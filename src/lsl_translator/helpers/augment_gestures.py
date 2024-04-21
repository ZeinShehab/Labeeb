import numpy as np
import random 
import itertools
import csv

data_directory = "data/"

# dataset = f'{data_directory}gesture_train.csv'
# augment_save_path = f'{data_directory}augmented_gestures_train.csv'

dataset = f'{data_directory}gesture_test.csv'
augment_save_path = f'{data_directory}augmented_gestures_test.csv'

EPS = 0.001
NUM_CLASSES = 2
SEQUENCE_FRAMES = 10
MULTI_HAND_LANDMARKS = 126
MAX_COL = (MULTI_HAND_LANDMARKS * SEQUENCE_FRAMES) + 1

TRAIN_ENTRIES_COUNT = 6
AUGMENTED_ENTRIES_COUNT = 60

x_values = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=list(range(1, MAX_COL, 3)))
y_values = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=list(range(2, MAX_COL, 3)))
z_values = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=list(range(3, MAX_COL, 3)))

def chunks(xs, n):
    n = max(1, n)
    return [xs[i:i+n] for i in range(0, len(xs), n)]

chunked_x_values = []
chunked_y_values = []
chunked_z_values = []

for i in range(NUM_CLASSES):
    gesture_x_chunks = []
    gesture_y_chunks = []
    gesture_z_chunks = []

    for j in range(TRAIN_ENTRIES_COUNT):
        gesture_x_chunks.append(chunks(x_values[i*TRAIN_ENTRIES_COUNT + j], 42))
        gesture_y_chunks.append(chunks(y_values[i*TRAIN_ENTRIES_COUNT + j], 42))
        gesture_z_chunks.append(chunks(z_values[i*TRAIN_ENTRIES_COUNT + j], 42))

    chunked_x_values.append(gesture_x_chunks)
    chunked_y_values.append(gesture_y_chunks)
    chunked_z_values.append(gesture_z_chunks)

augmented_gestures = []

for gesture_index in range(NUM_CLASSES):
    augmented_entries = [[] for _ in range(AUGMENTED_ENTRIES_COUNT)]

    for frame_idx in range(SEQUENCE_FRAMES):
        x_means = [0.0 for _ in range(42)]
        y_means = [0.0 for _ in range(42)]
        z_means = [0.0 for _ in range(42)]

        for keypoint_index in range(42):
            for train_entry_index in range(TRAIN_ENTRIES_COUNT):
                current_x_value = chunked_x_values[gesture_index][train_entry_index][frame_idx][keypoint_index]
                current_y_value = chunked_y_values[gesture_index][train_entry_index][frame_idx][keypoint_index]
                current_z_value = chunked_z_values[gesture_index][train_entry_index][frame_idx][keypoint_index]

                x_means[keypoint_index] += (current_x_value / TRAIN_ENTRIES_COUNT)
                y_means[keypoint_index] += (current_y_value / TRAIN_ENTRIES_COUNT)
                z_means[keypoint_index] += (current_z_value / TRAIN_ENTRIES_COUNT)
    
        # at this point we have the intervals for each keypoint
        for augment_count in range(AUGMENTED_ENTRIES_COUNT):
            augmented_frame = [[random.uniform(x_means[i] - EPS, x_means[i] + EPS),
                                random.uniform(y_means[i] - EPS, y_means[i] + EPS),
                                random.uniform(z_means[i] - EPS, z_means[i] + EPS)] for i in range(len(x_means))]
            
            if frame_idx == 0:
                augmented_frame[0] = [0.0, 0.0, 0.0]
            
            augmented_frame = list(itertools.chain.from_iterable(augmented_frame))
            augmented_entries[augment_count].append(augmented_frame)

    for i in range(AUGMENTED_ENTRIES_COUNT):
        augmented_entries[i] = list(itertools.chain.from_iterable(augmented_entries[i]))
    augmented_gestures.append(augmented_entries)


def logging_csv(number, landmark_list):
    if 0 <= number <= NUM_CLASSES:
        csv_path = augment_save_path
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    return

for i in range(NUM_CLASSES):
    for j in range(AUGMENTED_ENTRIES_COUNT):
        logging_csv(i, augmented_gestures[i][j])