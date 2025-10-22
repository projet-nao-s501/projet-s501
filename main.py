# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys
from scripts.meca_module.voice_recognition import test_text_to_speech, voice_recognition_sprint1  # TensorFlow is required for Keras to work
from scripts.meca_module.RobotMovement import marcheRobot

def main(session) :
    pass
import time
import cv2
import numpy as np

def main(session):
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
        cv2.imshow("Robot Camera", img2)
        
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)

        # # Mise en place motion_service
        # motion_service  = session.service("ALMotion")

        # # Wake up robot
        # motion_service.wakeUp()

        # # Marcher devant 
        # motion_service.moveToward(0.5, 0.0, 0.0, [["Frequency", 1.0]])
        # time.sleep(10)
        # motion_service.stopMove()

        # # Marcher derriere
        # motion_service.moveToward(-0.5, 0.0, 0.0, [["Frequency", 1.0]])
        # motion_service.stopMove()

        # # Mettre debout
        # posture_service = session.service("ALRobotPosture")
        # posture_service.goToPosture("StandInit", 1.0)



        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Unsubscribing...")
    video_service.unsubscribe(name_id)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contrôle du robot NAO.")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Adresse IP du robot NAO (ex: 192.168.x.x)")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi (par défaut: 9559)")
    parser.add_argument("--test", action="store_true",
                        help="Lancer uniquement le test TTS")

    args = parser.parse_args()
    session = qi.Session()

    try:
        session.connect(f"tcp://{args.ip}:{args.port}")
    except RuntimeError:
        print(f"Impossible de se connecter à NAOqi à l'adresse {args.ip}:{args.port}.")
        sys.exit(1)
    if args.test:
        test_text_to_speech(session)
    else:
        voice_recognition_sprint1(session)
    marcheRobot(session)
