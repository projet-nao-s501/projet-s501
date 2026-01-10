import cv2
import numpy as np
import pandas as pd

COLORS_DF = pd.read_csv("scripts/ia_module/couleurs.csv")

def detection_couleurs(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, valid_pixels_mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    meilleur_score = 0
    couleur_dominante = "Aucune"

    for _, row in COLORS_DF.iterrows():
        lower = np.array([row['h_min'], row['s_min'], row['v_min']])
        upper = np.array([row['h_max'], row['s_max'], row['v_max']])
        
        color_mask = cv2.inRange(hsv, lower, upper)
        
        final_mask = cv2.bitwise_and(color_mask, valid_pixels_mask)

        nb_pixels = cv2.countNonZero(final_mask)

        if nb_pixels > meilleur_score and nb_pixels > 300:
            meilleur_score = nb_pixels
            couleur_dominante = row['nom']
    
    
    return couleur_dominante