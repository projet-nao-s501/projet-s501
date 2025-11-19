import cv2
import numpy as np
import os
import tensorflow as tf

print("Répertoire actuel :", os.getcwd())

model = tf.keras.applications.MobileNetV2(weights="imagenet")

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

    # Prétraiter l'image
    resized = cv2.resize(image, (224, 224))
    recsized = tf.keras.preprocessing.image.img_to_array(resized)
    resized = tf.keras.applications.mobilenet_v2.preprocess_input(resized)

    # Prediction de l'image
    predictions = model.predict(np.array([resized]))
    decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=5)

    # Affichage résultatd

for _, label, score in decode_predictions[0] :
    print(f"Ceci est peut être {label} : probabilté {score*100}")

