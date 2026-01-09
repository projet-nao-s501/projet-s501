import numpy as np 
import cv2 


class detectionCouleur:
    
# lire l'image 
image = cv2.imread('images/boule.jpg',-1)
 #mettre le filtre 
image_hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
#mettre le masque 
masked= cv2.inRange(image_hsv,np.array([0, 0, 0]),np.array([180, 255, 100]))

result_black= cv2.bitwise_and(image, image, mask=masked)

#créer une fenetre qui peut etre redimensionnée
#cv2.namedWindow('image HSV', cv2.WINDOW_NORMAL)
# ajouter des dimensions
#cv2.resizeWindow('image HSV', 500, 400)

#afficher l'image
cv2.imshow('imageHSV', result_black)
cv2.waitKey(0)
cv2.destroyAllWindows()

