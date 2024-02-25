import os
import shutil

source_dir = "/Users/raedfidawi/LSL_Word_Images_v2"
train_dir = "/Users/raedfidawi/LSL_Word_Images_v2_Split/words_train"
test_dir = "/Users/raedfidawi/LSL_Word_Images_v2_Split/words_test"

# Add more classes as we add symbols
class_numbers = list(range(32, 37))
images_per_class = 840

# Takes 0...299 and 420...719 for train 
train_indices = list(range(300)) + list(range(420, 720))
# Takes 300...419 and 720...839 for train 
test_indices = list(range(300, 420)) + list(range(720, 840))

def organize_images():
    for class_number in class_numbers:
        for index in range(images_per_class):
            image_name = f"{class_number}_{index}.jpg"
            source_path = os.path.join(source_dir, image_name)

            if index in train_indices:
                destination_dir = train_dir
            elif index in test_indices:
                destination_dir = test_dir
            else:
                continue

            os.makedirs(destination_dir, exist_ok=True)
            destination_path = os.path.join(destination_dir, image_name)

            shutil.copy(source_path, destination_path)
            print(f"Copied {image_name} to {destination_dir}")

if __name__ == "__main__":
    organize_images()
