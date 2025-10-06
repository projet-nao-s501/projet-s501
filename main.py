# -*- encoding: UTF-8 -*-

# Lien pour utiliser le flux vidéo et entraîner un modèle :
# https://teachablemachine.withgoogle.com/

# Packages requis :
# pip install tensorflow==2.12.1 numpy==1.23.5 opencv-python==4.9.0.80

import qi
import argparse
import sys
import time
#import almath
import numpy as np
import cv2
# from keras.models import load_model  # À activer si tu utilises un modèle IA

# ======================================
# === CLASSE DE DEPLACEMENT DU ROBOT ===
# ======================================

class MyClass:
    def __init__(self):
        self.positionErrorThresholdPos = 0.01
        self.positionErrorThresholdAng = 0.03
        self.motion = None

    def session(self):
        # TODO : définir ou surcharger cette méthode pour récupérer la session,
        # ou injecter la session dans la classe avant usage
        raise NotImplementedError("La méthode session() doit être définie pour accéder aux services.")

    def onLoad(self):
        self.motion = self.session().service("ALMotion")

    def onUnload(self):
        if self.motion:
            self.motion.moveToward(0.0, 0.0, 0.0)

    class Pose2D:
        def __init__(self, x=0, y=0, theta=0):
            self.x = x
            self.y = y
            self.theta = theta

        def rotation_matrix(self):
            c = np.cos(self.theta)
            s = np.sin(self.theta)
            return np.array([[c, -s],
                             [s,  c]])

        def __mul__(self, other):
            new_pos = np.array([self.x, self.y]) + self.rotation_matrix() @ np.array([other.x, other.y])
            new_theta = self.theta + other.theta
            return MyClass.Pose2D(new_pos[0], new_pos[1], new_theta)

        def diff(self, other):
            dx = self.x - other.x
            dy = self.y - other.y
            dtheta = self.theta - other.theta
            return MyClass.Pose2D(dx, dy, dtheta)

        def toVector(self):
            return [self.x, self.y, self.theta]

    def modulo2PI(self, theta):
        return theta % (2 * np.pi)

    def getParameter(self, param_name):
        # TODO : remplacer par ta méthode de récupération des paramètres
        raise NotImplementedError("La méthode getParameter() doit être définie pour récupérer les paramètres.")

    def onInput_onStart(self):
        robot_pos = self.motion.getRobotPosition(True)  # [x, y, theta]
        init_position = self.Pose2D(robot_pos[0], robot_pos[1], robot_pos[2])

        distance_x = self.getParameter("Distance X (m)")
        distance_y = self.getParameter("Distance Y (m)")
        theta_deg = self.getParameter("Theta (deg)")
        theta_rad = np.deg2rad(theta_deg)

        target_distance = self.Pose2D(distance_x, distance_y, theta_rad)
        expected_end_position = init_position * target_distance

        enable_arms = self.getParameter("Arms movement enabled")
        self.motion.setMoveArmsEnabled(enable_arms, enable_arms)

        self.motion.moveTo(distance_x, distance_y, theta_rad)

        robot_pos_end = self.motion.getRobotPosition(False)
        real_end_position = self.Pose2D(robot_pos_end[0], robot_pos_end[1], robot_pos_end[2])

        position_error = real_end_position.diff(expected_end_position)
        position_error.theta = self.modulo2PI(position_error.theta)

        if (
            abs(position_error.x) < self.positionErrorThresholdPos and
            abs(position_error.y) < self.positionErrorThresholdPos and
            abs(position_error.theta) < self.positionErrorThresholdAng
        ):
            self.onArrivedAtDestination()
        else:
            self.onStoppedBeforeArriving(position_error.toVector())

    def onArrivedAtDestination(self):
        # TODO : implémente ce qu’il faut faire quand on arrive
        print("Arrivé à destination.")

    def onStoppedBeforeArriving(self, error_vector):
        # TODO : implémente ce qu’il faut faire en cas d’arrêt prématuré
        print(f"Arrêt avant arrivée, erreur: {error_vector}")
# ============================
# === CODE PRINCIPAL MAIN() ===
# ============================

def main(session):
    # === Initialisation des services ===
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    # video_service = session.service("ALVideoDevice")

    # === (Commenté) Con pythonfiguration caméra & modèle IA ===
    # resolution = 2  # VGA (640x480)
    # color_space = 11  # RGB
    # fps = 15
    # camera_index = 1

    # np.set_printoptions(suppress=True)
    # model = load_model("keras_model.h5", compile=False)
    # class_names = open("labels.txt", "r").readlines()

    # === (Commenté) Gestion des abonnements vidéo ===
    # subscribers = video_service.getSubscribers()
    # for name in subscribers:
    #     try:
    #         video_service.unsubscribe(name)
    #         print("Unsubscribed:", name)
    #     except Exception as e:
    #         print("Error unsubscribing", name, ":", e)

    # name_id = video_service.subscribeCamera("", camera_index, resolution, color_space, fps)
    # print("Subscribed to camera:", name_id)

    # === Réveil et posture initiale ===
    motion_service.wakeUp()
    posture_service.goToPosture("StandInit", 1.0)

    print("Robot prêt. Appuyez sur Ctrl+C pour arrêter.")

    try:
        while True:
            # === (Commenté) Lecture d'image depuis caméra NAO ===
            # image = video_service.getImageRemote(name_id)
            # if image is None:
            #     print("No image.")
            #     continue

            # width, height = image[0], image[1]
            # array = image[6]
            # img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
            # img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # cv2.imshow("Robot Camera", img_bgr)

            # === (Commenté) Prétraitement image pour IA ===
            # img_resized = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
            # img_array = np.asarray(img_resized, dtype=np.float32).reshape(1, 224, 224, 3)
            # img_array = (img_array / 127.5) - 1
            # prediction = model.predict(img_array)
            # index = np.argmax(prediction)
            # class_name = class_names[index]
            # confidence_score = prediction[0][index]
            # print("Class:", class_name[2:], "Confidence:", np.round(confidence_score * 100, 2), "%")

            # === Exemple de mouvement vers l'avant ===
            motion_service.moveToward(0.5, 0.0, 0.0, [["Frequency", 1.0]])
            time.sleep(5)
            motion_service.stopMove()

            # Pause entre les boucles
            time.sleep(2)

            # Pour test uniquement une fois
            break

    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur.")

    # Nettoyage
    # video_service.unsubscribe(name_id)
    # cv2.destroyAllWindows()
    motion_service.rest()


# =======================
# === Lancement script ===
# =======================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Adresse IP du robot NAO (ex: 192.168.x.x)")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi (par défaut: 9559)")

    args = parser.parse_args()
    session = qi.Session()

    try:
        session.connect(f"tcp://{args.ip}:{args.port}")
    except RuntimeError:
        print(f"Impossible de se connecter à NAOqi à l'adresse {args.ip}:{args.port}.")
        sys.exit(1)

    main(session)
