import numpy as np
import random 
import itertools
import csv

data_directory = "data/"
train_dataset = f'{data_directory}gesture_train.csv'
test_dataset = f'{data_directory}gesture_test.csv'
# augment_save_path = f'{data_directory}augmented_gestures_train.csv'
augment_save_path = f'{data_directory}augmented_gestures_train.csv'

NUM_CLASSES = 2
SEQUENCE_FRAMES = 10
TRAIN_ENTRIES_PER_GESTURE = 10
MULTI_HAND_LANDMARKS = 126
MAX_COL = (MULTI_HAND_LANDMARKS * SEQUENCE_FRAMES) + 1
AUGMENTED_ENTRIES_COUNT = 100

x_values = np.loadtxt(train_dataset, delimiter=',', dtype='float32', usecols=list(range(1, MAX_COL, 3)))
y_values = np.loadtxt(train_dataset, delimiter=',', dtype='float32', usecols=list(range(2, MAX_COL, 3)))
z_values = np.loadtxt(train_dataset, delimiter=',', dtype='float32', usecols=list(range(3, MAX_COL, 3)))

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

    for j in range(TRAIN_ENTRIES_PER_GESTURE):
        gesture_x_chunks.append(chunks(x_values[i*TRAIN_ENTRIES_PER_GESTURE + j], 42))
        gesture_y_chunks.append(chunks(y_values[i*TRAIN_ENTRIES_PER_GESTURE + j], 42))
        gesture_z_chunks.append(chunks(z_values[i*TRAIN_ENTRIES_PER_GESTURE + j], 42))

    chunked_x_values.append(gesture_x_chunks)
    chunked_y_values.append(gesture_y_chunks)
    chunked_z_values.append(gesture_z_chunks)


# gesture_index | train_entry_index | frame_index | keypoint_index
print(chunked_x_values[0][2][0][1])


augmented_gestures = []

for gesture_index in range(NUM_CLASSES):
    augmented_entries = [[] for _ in range(AUGMENTED_ENTRIES_COUNT)]

    for frame_idx in range(SEQUENCE_FRAMES):
        x_intervals = [[99999999, -99999999] for _ in range(42)]
        y_intervals = [[99999999, -99999999] for _ in range(42)]
        z_intervals = [[99999999, -99999999] for _ in range(42)]

        for keypoint_index in range(42):
            for train_entry_index in range(TRAIN_ENTRIES_PER_GESTURE):
                current_x_value = chunked_x_values[gesture_index][train_entry_index][frame_idx][keypoint_index]
                current_y_value = chunked_y_values[gesture_index][train_entry_index][frame_idx][keypoint_index]
                current_z_value = chunked_z_values[gesture_index][train_entry_index][frame_idx][keypoint_index]

                x_intervals[keypoint_index][0] = min(current_x_value, x_intervals[keypoint_index][0])
                x_intervals[keypoint_index][1] = max(current_x_value, x_intervals[keypoint_index][1])

                y_intervals[keypoint_index][0] = min(current_y_value, y_intervals[keypoint_index][0])
                y_intervals[keypoint_index][1] = max(current_y_value, y_intervals[keypoint_index][1])
                
                z_intervals[keypoint_index][0] = min(current_z_value, z_intervals[keypoint_index][0])
                z_intervals[keypoint_index][1] = max(current_z_value, z_intervals[keypoint_index][1])
    
        # at this point we have the intervals for each keypoint
        eps = 0.001
        for augment_count in range(AUGMENTED_ENTRIES_COUNT):
            augmented_frame = [[random.uniform(x_intervals[i][0], x_intervals[i][1]),
                                random.uniform(y_intervals[i][0], y_intervals[i][1]),
                                random.uniform(z_intervals[i][0], z_intervals[i][1])] for i in range(len(x_intervals))]
            augmented_frame = list(itertools.chain.from_iterable(augmented_frame))
            
            # for i in range(42):
            #     mid_x = (x_intervals[i][0] + x_intervals[i][1])/2
            #     mid_y = (y_intervals[i][0] + y_intervals[i][1])/2
            #     mid_z = (z_intervals[i][0] + z_intervals[i][1])/2
            #     augmented_frame = [random.uniform(mid_x - eps, mid_x + eps),
            #                         random.uniform(mid_y - eps, mid_y + eps),
            #                         random.uniform(mid_z - eps, mid_z + eps)]
            augmented_entries[augment_count].append(augmented_frame)

    for i in range(AUGMENTED_ENTRIES_COUNT):
        augmented_entries[i] = list(itertools.chain.from_iterable(augmented_entries[i]))
    augmented_gestures.append(augmented_entries)


def logging_csv(number, landmark_list):
    if 0 <= number <= NUM_CLASSES:
        csv_path = augment_save_path
        # csv_path = 'data/train.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    return

for i in range(NUM_CLASSES):
    for j in range(AUGMENTED_ENTRIES_COUNT):
        logging_csv(i, augmented_gestures[i][j])

# x_data_0 = np.array_split(x_values[0], SEQUENCE_FRAMES)

# print(x_data_0)