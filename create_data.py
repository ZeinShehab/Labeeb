import os


images_dir = "D:/archive-unaug/unaugmented/416/train/images"
labels_dir = "D:/archive-unaug/unaugmented/416/train/labels"

labels = os.listdir(labels_dir)
images = os.listdir(images_dir)

image_count = [-1 for _ in range(28)]


for image in images:
    image_name = image.split('.jpg')[0]
    label_name = image_name + '.txt'

    try:
        label_index = labels.index(label_name)
    except ValueError:
        continue

    if label_index >= 0:
        image_index = int(open(os.path.join(labels_dir, label_name), "r").read().split(' ')[0])
        
        if (image_index == 0 and image_count[image_index] == 464):
            image_index = 24
        
        image_count[image_index] += 1

        os.rename(os.path.join(images_dir, f"{image_name}.jpg"), os.path.join(images_dir, f"{image_index}_{image_count[image_index]}.jpg"))
        os.rename(os.path.join(labels_dir, label_name), os.path.join(labels_dir, f"{image_index}_{image_count[image_index]}.txt"))


print(image_count)

# with open("labels.csv", "w+") as csv:
#     for filename in (os.listdir("labels"))[::-1]:
#         datafile = open(os.path.join("labels", filename), "r")
#         # csv.write(datafile.read() + "\n")

#         print(datafile.read().split(' ')[0])
#         datafile.close()
