import cv2
import numpy as np

# tab = [teinte, saturation, luminosité]


# Test de la caméra avec opencv pour la detection de couleur 

# Ouvrir la webcam (0 = webcam par défaut, 1 = autre caméra si branchée)
def detectionRouge() : 
    cap = cv2.VideoCapture(0)

    # ici ret c'est pour retiourner un booléan qui va dire si la capture de l'image est bien 
    # ici frame est l'image capturer par la webcam
    while True:
        ret, frame = cap.read() # Récupère une image
        if not ret:
            break
        
        # Affiche l'image
        cv2.imshow("Webcam", frame)
        
        # 1er intervalle : rouge de 0 à 10
        lower_red1 = np.array([0, 25, 25])
        upper_red1 = np.array([10, 255, 255])
        # 2ème intervalle : rouge de 170 à 180
        lower_red2 = np.array([170, 25, 25])
        upper_red2 = np.array([180, 255, 255])

        # Création des deux masques
        mask1 = cv2.inRange(frame, lower_red1, upper_red1)
        mask2 = cv2.inRange(frame, lower_red2, upper_red2)

        # Fusion des deux masques
        mask = mask1 | mask2
        
        result_webcam = cv2.bitwise_and(frame,frame,mask=mask)

            # Affiche l'image
        cv2.imshow("Webcam de l'ordinateur", result_webcam)

        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()



