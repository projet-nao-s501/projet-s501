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

# Fonctions ajoutés par Junior pour 
# l'intégration entre détection couleur
# et reconnaissance vocale.
# Les fonctions qui suivent permettent de
# déterminer si une couleur est réellement
# présente (n'affiche pas juste un filtre
# visuel)

def analyser_masque(mask, seuil_pourcentage=1.5):
    """
    Analyse un masque pour déterminer si
    assez de pixels sont détectés.
    La fonction compte le nbre de pixels
    non-noirs dans le masque. Si ce nbre
    dépasse le seuil en %, on considère
    que la couleur est prèsente et la
    fonction retourne True.
    """

    # On compte les pixels non-noirs 
    # (pixels de la couleur détectée)
    pixels_detectes = cv2.countNonZero(mask)

    # Calcul du total de pixels de l'image
    hauteur, largeur = mask.shape[:2]
    total_pixels = hauteur * largeur

    # Calcul du pourcentage
    pourcentage = (pixels_detectes / total_pixels) * 100

    # A décommenter pour le debug
    # print(f"[DEBUG] Pixels détectés: {pixels_detectes}/{total_pixels} ({pourcentage:.2f}%)")
    
    return pourcentage >= seuil_pourcentage

def detecter_couleur(frame, seuil_pourcentage=1.5):
    """
    Détecte quelle couleur (rouge, noir, ...)
    est présente dans l'image.
    Cette fonction est le point d'entrée 
    principal pour la détection.
    Elle teste chaque couleur et retourne
    le nom de la première détectée.
    Pour l'instant, elle va retourne
    "rouge" si le rouge est détecté
    et "None" dans les autres cas. 
    A adapter quand il y'aura d'autres
    couleurs.
    """

    # Test du rouge
    masque_rouge = detectionRouge(frame)
    masque_rouge_gray = cv2.cvtColor(masque_rouge, cv2.COLOR_BGR2GRAY)
    
    if analyser_masque(masque_rouge_gray, seuil_pourcentage):
        return "red"
    
    return None



