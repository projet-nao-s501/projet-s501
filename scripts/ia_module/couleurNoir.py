import numpy as np 
import cv2 

# Ouvrir la webcam (0 = webcam par défaut, 1 = autre caméra si branchée)



# ici ret c'est pour retiourner un booléan qui va dire si la capture de l'image est bien 
# ici frame est l'image capturer par la webcam
def detectionCouleurNoir() :
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    while True:
        ret, frame = cap.read() # Récupère une image
        if not ret:
            print("Impossible de lire l'image depuis la webcam")
            break

        # tab = [teinte, saturation, luminosité]
        # 1er intervalle : rouge de 0 à 10
        lower = np.array([0, 0, 200])    
        upper = np.array([180, 30, 255])


        # convertir l'image en HVG
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Création des deux masques
        mask = cv2.inRange(hsv, lower, upper)    
        # Fusion des deux masques
        mask = mask

        result_webcam = cv2.bitwise_and(frame,frame,mask=mask)

        # Affiche l'image
        cv2.imshow("Webcam de l'ordinateur", result_webcam)

           # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
	
