import cv2
import numpy as np

# tab = [teinte, saturation, luminosité]


# Test de la caméra avec opencv pour la detection de couleur 

# Ouvrir la webcam (0 = webcam par défaut, 1 = autre caméra si branchée)
def detectionRouge(frame) : 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 1er intervalle : rouge de 0 à 10
    lower_red1 = np.array([0, 25, 25])
    upper_red1 = np.array([10, 255, 255])
    # 2ème intervalle : rouge de 170 à 180
    lower_red2 = np.array([170, 25, 25])
    upper_red2 = np.array([180, 255, 255])

    # Création des deux masques
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Fusion des deux masques
    mask = mask1 | mask2
    
    result_webcam = cv2.bitwise_and(frame,frame,mask=mask)

    return result_webcam



