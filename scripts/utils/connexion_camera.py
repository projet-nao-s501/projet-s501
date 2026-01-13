import cv2
import numpy as np
from scripts.ia_module.detection_couleurs import detection_couleurs_Camera

def connexionCamera(session):
    video_service = session.service("ALVideoDevice")
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

    while True:
        image = video_service.getImageRemote(name_id)
        if image is None:
            print("No image.")
            continue

        width, height = image[0], image[1]
        array = image[6]
        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

        img2 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # fonction sur IA 
        result = detection_couleurs_Camera(img2)
        cv2.namedWindow("Detection couleurs", cv2.WINDOW_NORMAL)
        cv2.imshow("Detection couleurs", result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Unsubscribing...")
    video_service.unsubscribe(name_id)
    cv2.destroyAllWindows()