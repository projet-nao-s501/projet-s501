import cv2
import numpy as np

# numpy array = librairie qui manipule les tableaux.

#charger une image (prend 2 paramètres (le chemin de l'image)/(le mode d'ouverture))
#img = cv2.imread("images/Pomme_test.jpg",cv2.IMREAD_COLOR)
img = cv2.imread("images/les_amies.webp",cv2.IMREAD_COLOR)

# pour redéfinir la taille de l'image 
img = cv2.resize(img,(500,500))

# pour la rotation de l'image(prend 2 paramètres (l'image )/(la rotation))
#img = cv2.rotate(img, cv2.ROTATE_180)

# pour suavegarder une image 
cv2.imwrite('new.jpg',img)

# afficher une image(prend 2 paramètres (nom de la fenetre qui affiche notre images)/(l'image que l'on veux charger))
#cv2.imshow("Une pomme",img)

# pour laiser un image durer 5 min ( tant que le clavier n'a pas été toucher)
cv2.waitKey(0)

# pour supprimer toutes les fenetres 
cv2.destroyAllWindows()

#-----------------------------------------------------------------------------------------------

#COULEUR ET DETECTION DE LA COULEUR DANS UNE IMAGE

#Etape 1 (ON MET LES COULEUR EN HSV SE L'IMAGE)
# pour (prend 2 paramètres (image en question)/(la convertion de l'image))

image_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
cv2.resize(image_hsv,(500,500))
#cv2.imshow("Une pomme",image_hsv)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#ETAPE 2 (ISOLER LA COULEUR CHOSIS (ROUGE) avec un masque binaire)
#un masque binaire c'est lorsque la couleur que l'on veux sera en blanc et le reste en noir.

# tab = [teinte, saturation, luminosité]

# 1er intervalle : rouge de 0 à 10
lower_red1 = np.array([0, 25, 25])
upper_red1 = np.array([10, 255, 255])
# 2ème intervalle : rouge de 170 à 180
lower_red2 = np.array([170, 25, 25])
upper_red2 = np.array([180, 255, 255])

# Création des deux masques
mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)

# Fusion des deux masques
mask = mask1 | mask2

#cv2.imshow("Image sous masque binaire", mask)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#on va recupere juste la couleur de l'image avec la fonction bitwise_and 

result_red = cv2.bitwise_and(img,img,mask=mask)
cv2.namedWindow('image_hsv', cv2.WINDOW_NORMAL)

cv2.imshow("Image avce les deux maques appliqués", result_red)
cv2.waitKey(0)
cv2.destroyAllWindows()


