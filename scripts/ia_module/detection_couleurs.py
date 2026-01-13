import cv2
import numpy as np
import pandas as pd


def detection_couleurs_Camera(frame):
    # Charger le fichier CSV des plages HSV
    colors_df = pd.read_csv("scripts/ia_module/couleurs.csv")

    # Conversion en HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    detected_colors = []

    # Parcours de chaque couleur du CSV
    for _, row in colors_df.iterrows():
        lower = np.array([row['h_min'], row['s_min'], row['v_min']])
        upper = np.array([row['h_max'], row['s_max'], row['v_max']])
        mask = cv2.inRange(hsv, lower, upper)

        # Si assez de pixels détectés → couleur présente
        if cv2.countNonZero(mask) > 500:
            detected_colors.append(row['nom'])

    # Préparation du texte affiché sur l’image
    text = " | ".join(set(detected_colors)) if detected_colors else "Aucune couleur détectée"

    # Écriture sur l’image
    x, y = 10, 30
    line_h = 25
    max_per_line = 4

    for i in range(0, len(detected_colors), max_per_line):
        line = " | ".join(detected_colors[i:i+max_per_line])
        cv2.putText(frame, line, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        y += line_h



    # Retourne l’image annotée 
    return frame