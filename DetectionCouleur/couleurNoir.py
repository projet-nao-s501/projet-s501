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

#----------------------------------------
# Test de la caméra avec opencv pour la detection de couleur 

# Ouvrir la webcam (0 = webcam par défaut, 1 = autre caméra si branchée)
cap = cv2.VideoCapture(0)

# ici ret c'est pour retourner un booléan qui va dire si la capture de l'image est bien 
# ici frame est l'image capturer par la webcam
while True:
    ret, frame = cap.read() # Récupère une image
    if not ret:
        break
     # Affiche l'image
    cv2.imshow("Webcam", frame)

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

