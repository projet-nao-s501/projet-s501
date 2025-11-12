import cv2
import numpy as np
import pandas as pd


def detection_couleurs () :
    # Charger le fichier CSV avec les plages de couleurs
    colors_df = pd.read_csv("scripts/ia_module/couleurs.csv")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
    
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detected_colors = []
    
        for _, row in colors_df.iterrows():
            lower = np.array([row['h_min'], row['s_min'], row['v_min']])
            upper = np.array([row['h_max'], row['s_max'], row['v_max']])
            mask = cv2.inRange(hsv, lower, upper)
    
            if cv2.countNonZero(mask) > 500:  # seuil pour éviter le bruit
                detected_colors.append(row['nom'])
    
        # Affichage du texte sur l’image
        text = " | ".join(set(detected_colors)) if detected_colors else "Aucune couleur détectée"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
        cv2.imshow("Detection de couleurs", frame)
    
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
