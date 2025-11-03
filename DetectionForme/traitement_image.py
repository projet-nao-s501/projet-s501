import cv2
import numpy as np
import os
print("Répertoire actuel :", os.getcwd())


while True :
    image = cv2.imread('DetectionForme/images/128491_01.jpg')

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    l_b = np.array([110, 0, 0])
    u_b = np.array([255, 255, 255])

    mask = cv2.inRange(hsv, l_b, u_b)

    res = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow("image", image)
    cv2.imshow("mask", mask)
    cv2.imshow("res", res)

    key = cv2.waitKey(1)
    if key == 27 :
        break


