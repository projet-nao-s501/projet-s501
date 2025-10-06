import numpy as np 
import cv2 

#------------------Image noire--------------------------------------------------------------------------
# lire l'image 
image = cv2.imread("DetectionCouleur/images/boule.jpg",-1)
 #mettre le filtre 
image_hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
#mettre le masque 
masked= cv2.inRange(image_hsv,np.array([0, 0, 0]),np.array([180, 255, 100]))

result_black= cv2.bitwise_and(image, image, mask=masked)


#afficher l'image
#cv2.imshow('imageHSV', result_black)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#---------------------------image blanche ---------------------------------------------------------
# lire l'image 
image1 = cv2.imread("DetectionCouleur/images/les_amies.webp",-1)
 #mettre le filtre 
image_hsv1 = cv2.cvtColor(image1,cv2.COLOR_BGR2HSV)
#mettre le masque 
masked1= cv2.inRange(image_hsv1,np.array([0, 0, 200]),np.array([180, 30, 255]))

result_black1= cv2.bitwise_and(image1, image1, mask=masked1)


#afficher l'image
#cv2.imshow('imageHSV', result_black1)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#----------------------------------------------Acces camera ---------------------------------------------

# Test de la caméra avec opencv pour la detection de couleur 

# Ouvrir la webcam (0 = webcam par défaut, 1 = autre caméra si branchée)
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)


# ici ret c'est pour retiourner un booléan qui va dire si la capture de l'image est bien 
# ici frame est l'image capturer par la webcam
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
	
