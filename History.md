- We tried saving landmarks for the hand and training these landmarks. It wasn't very accurate (40%)

- We tried using the augmented RGB images as input into a CNN. Very low accuracy (0.03%)

- We tried other unaugmented RGB images as input. Similar results. Very low accuracy (0.03%)

- We tried converting the RGB images into binary colored images (Skin: Black, Background: White). Conversion process was extremely inaccurate with the available datasets.

- We trained the neural network on a dataset of binary images and it gave very high accuracy

- We added the Z coordinate to the keypoint classifier and it improved accuracy to 87%