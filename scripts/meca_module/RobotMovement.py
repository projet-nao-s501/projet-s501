import numpy as np
import time
import qi

try :
    from .sonar_detection import SonarDetection
except Exception as e :
    e.add_note("Erreur lors de l'import du package")
    raise e

class RobotMovement:
    def __init__(self, motion):
        # Seuils d'erreur pour considérer le déplacement réussi
        self.positionErrorThresholdPos = 0.01  # 1 cm
        self.positionErrorThresholdAng = 0.03  # ~1.7 degrés
        self.motion = motion

    def onUnload(self):
        """
        Stoppe tout mouvement du robot.
        """
        if self.motion:
            self.motion.moveToward(0.0, 0.0, 0.0)

    class Pose2D:
        """
        Représentation d'une position 2D avec orientation.
        """

        def __init__(self, x : float = 0, y : float = 0, theta : float = 0):
            self.x :float = x
            self.y : float = y
            self.theta : float = theta

        def rotation_matrix(self):
            """
            Matrice de rotation 2D pour orientation theta.
            """
            c = np.cos(self.theta)
            s = np.sin(self.theta)
            return np.array([[c, -s],
                             [s,  c]])

        def __mul__(self, other):
            """
            Composition de transformations : self * other.
            """
            new_pos = np.array([self.x, self.y]) + self.rotation_matrix() @ np.array([other.x, other.y])
            new_theta = self.theta + other.theta
            return RobotMovement.Pose2D(new_pos[0], new_pos[1], new_theta)

        def __sub__(self, other):
            """
            Différence entre deux poses : self - other.
            """
            dx = self.x - other.x
            dy = self.y - other.y
            dtheta = self.theta - other.theta
            return RobotMovement.Pose2D(dx, dy, dtheta)

        def toVector(self):
            """
            Convertit la pose en liste [x, y, theta].
            """
            return [self.x, self.y, self.theta]

    def modulo2PI(self, theta):
        """
        Normalise un angle entre 0 et 2*pi.
        """
        return theta * np.pi / 180

    def onInput_onStart(self, distance_x, distance_y ,theta_rad):
        """
        Lance le déplacement du robot selon paramètres donnés.
        Vérifie la position finale et déclenche les callbacks correspondants.
        """
        # Récupération de la position initiale réelle du robot
        robot_pos = self.motion.getRobotPosition(True)  # [x, y, theta]
        init_position = self.Pose2D(robot_pos[0], robot_pos[1], robot_pos[2])

        # Calcul de la position cible attendue
        target_distance = self.Pose2D(robot_pos[0]+distance_x, robot_pos[1]+distance_y, theta_rad)
        expected_end_position = init_position * target_distance

        # Commande de déplacement
        self.motion.moveTo(target_distance.toVector()[0],target_distance.toVector()[1], theta_rad)

        # Lecture de la position finale réelle
        robot_pos_end = self.motion.getRobotPosition(False)
        real_end_position = self.Pose2D(robot_pos_end[0], robot_pos_end[1], robot_pos_end[2])

        # Calcul de l'erreur entre attendu et réel
        position_error = real_end_position - expected_end_position
        position_error.theta = self.modulo2PI(position_error.theta)

        # Vérification de l'erreur pour confirmer l'arrivée ou l'arrêt prématuré
        if (
            abs(position_error.x) < self.positionErrorThresholdPos and
            abs(position_error.y) < self.positionErrorThresholdPos and
            abs(position_error.theta) < self.positionErrorThresholdAng
        ):
            self.onArrivedAtDestination()
        else:
            self.onStoppedBeforeArriving(position_error.toVector())

    def onArrivedAtDestination(self):
        """
        Callback à définir pour gestion à l'arrivée à destination.
        """
        print("Arrivé à destination.")

    def onStoppedBeforeArriving(self, error_vector):
        """
        Callback à définir en cas d'arrêt prématuré.
        """
        print(f"Arrêt avant arrivée, erreur: {error_vector}")


def marcheRobot(session):
    """
    Fonction principale qui initialise les services,
    active la posture initiale, puis effectue un déplacement.
    """

    # Initialisation des services
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    motion_service.wakeUp()
    posture_service.goToPosture("StandInit", 1.0)
    
    print("Robot prêt. Appuyez sur Ctrl+C pour arrêter.")
    try:
        motion_service.moveToward(0.125,0.125,0.0,[["Frequency",1.0]])
        while True:
            motionAlert = 0.42
            robotMouvement = RobotMovement(motion_service)
            pos2D = robotMouvement.Pose2D(x=0.5,y=0,theta=0)
            _,_,theta = pos2D.toVector()
            right, left = SonarDetection(session,motionAlert)
            while left != -1 or right != -1 :
                isStoped = motion_service.stopMove()
                if  left != -1 : theta -= robotMouvement.modulo2PI(2.5)
                else : theta += robotMouvement.modulo2PI(2.5)
                if -1.0 < theta < 1.0 :
                    right, left = SonarDetection(session,motionAlert)
                    if isStoped : 
                        motion_service.moveToward(0.005,0.005,theta,[["Frequency",0.5]])
                        time.sleep(2)
                        motion_service.stopMove()
                else : break
            if theta < -1  : theta = -1
            elif theta > 1 : theta = 1
            if not(motion_service.moveIsActive()) : motion_service.moveToward(0.125,0.125,0.0,[["Frequency",1.0]])
    except Exception as e :
        raise e

