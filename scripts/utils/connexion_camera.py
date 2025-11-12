import cv2
import numpy as np
from scripts.ia_module.traitement_image import detectionRouge, detecter_couleur

# Ajouts faits par Junior pour
# l'intégration de la détection vocale.
# Ajouts : 
# - Import de detecter_couleur 
# depuis traitement_image
# - Ajout des services ALMemory et 
# ALTextToSpeech
# - Analyse automatique des frames 
# pour détecter les couleurs
# - Stockage dans ALMemory pour 
# communication avec module vocal
# - Annonce vocale automatique 
# "J'ai détecté une couleur"

def connexionCamera(session):
    video_service = session.service("ALVideoDevice")
    
    # Stocker la couleur détectée
    memory = session.service("ALMemory") 
    # Pour parler
    tts = session.service("ALTextToSpeech")
    tts.setLanguage("English") # config en français

    # Camera settings
    resolution = 1  # VGA (640x480)
    color_space = 11  # RGB
    fps = 30
    camera_index = 1  # Use 0 or 1 depending on which one works

    np.set_printoptions(suppress=True)

    subscribers = video_service.getSubscribers()
    print("Abonnements actifs :", subscribers)

    # Forcer le desabonnement de tous
    for name in subscribers:
        try:
            video_service.unsubscribe(name)
            print("Desabonne :", name)
        except Exception as e:
            print("Erreur lors du desabonnement de", name, ":", e)

    # Subscribe
    name_id = ""
    name_id = video_service.subscribeCamera(name_id, camera_index, resolution, color_space, fps)
    print("Subscribed to camera:", name_id)
    # Variable pour éviter de répéter l'annonce à chaque frame
    derniere_couleur_annoncee = None

    while True:
        image = video_service.getImageRemote(name_id)
        if image is None:
            print("No image.")
            continue

        width, height = image[0], image[1]
        array = image[6]
        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

        img2 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Appel de la fonction detecter_couleur
        # pour analyser l'image
        couleur_detectee = detecter_couleur(img2, seuil_pourcentage=10)

        if couleur_detectee:
            # Stocker la couleur dans ALMemory 
            # pour le module vocal
            memory.insertData("CouleurDetectee", couleur_detectee)
            print(f"[INFO] Couleur détectée et stockée : {couleur_detectee}")
            
            # Annoncer uniquement si c'est une 
            # nouvelle couleur (évite 
            # de répéter "J'ai détecté 
            # une couleur" à chaque 
            # frame)
            if couleur_detectee != derniere_couleur_annoncee:
                tts.say("I detected a color")
                print(f"[VOCAL] NAO annonce : 'I detected a color'")
                derniere_couleur_annoncee = couleur_detectee
        else:
            # Aucune couleur détectée : réinitialiser
            memory.insertData("CouleurDetectee", None)
            derniere_couleur_annoncee = None
        
        # Affichage visuel (comme avant)
        result = detectionRouge(img2)
        cv2.imshow("Detection du rouge", result)
        
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Unsubscribing...")
    video_service.unsubscribe(name_id)
    cv2.destroyAllWindows()