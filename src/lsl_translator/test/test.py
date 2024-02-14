from mediapipe_helper import MediaPipe
import cv2 as cv

mp = MediaPipe()
image = cv.imread("C:/Users/zeins/LSL_Translator/helpers/test_image3.jpg")

# cv.imshow("image", image)
# cv.waitKey(0)

multi_hand_landmarks = mp.get_multi_hand_landmarks(image)
print(multi_hand_landmarks)