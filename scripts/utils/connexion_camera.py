import cv2
import numpy as np
from scripts.meca_module.nao_final import autonomous_exploration, initialiser_exploration
from scripts.ia_module.traitement_image import detectionRouge, detecter_couleur
from scripts.ia_module.vocal.voice_recognition_2 import voice_recognition_2

def connexionCamera(session,tab):
    video_service = session.service("ALVideoDevice")
    
    # Stocker la couleur détectée
    memory = session.service("ALMemory") 
    # Pour parler
    tts = session.service("ALTextToSpeech")
    asr = session.service("ALSpeechRecognition")
    tts.setLanguage("French") # config en français

    # Camera settings
    resolution = 1  # VGA (640x480)
    color_space = 13  # RGB
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

    initialiser_exploration(session)

    while True:
        image = video_service.getImageRemote(name_id)
        if image is None:
            print("No image.")
            continue

        width, height = image[0], image[1]
        array = image[6]

        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

        win = autonomous_exploration(session, img, video_service, name_id, tab)
        if win == 0 :
            return
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Unsubscribing...")
    video_service.unsubscribe(name_id)
    cv2.destroyAllWindows()