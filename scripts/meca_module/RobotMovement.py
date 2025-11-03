import numpy as np
import time
from .sonar_detection import SonarDetection

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

    def getParameter(self, param_name):
        """
        TODO : Implémenter la récupération des paramètres selon contexte.
        Par exemple via une interface utilisateur ou configuration.
        """
        raise NotImplementedError("La méthode getParameter() doit être définie pour récupérer les paramètres.")

    def onInput_onStart(self):
        """
        Lance le déplacement du robot selon paramètres donnés.
        Vérifie la position finale et déclenche les callbacks correspondants.
        """
        # Récupération de la position initiale réelle du robot
        robot_pos = self.motion.getRobotPosition(True)  # [x, y, theta]
        init_position = self.Pose2D(robot_pos[0], robot_pos[1], robot_pos[2])

        # Récupération des paramètres de déplacement
        distance_x = self.getParameter("Distance X (m)")
        distance_y = self.getParameter("Distance Y (m)")
        theta_deg = self.getParameter("Theta (deg)")
        theta_rad = np.deg2rad(theta_deg)

        # Calcul de la position cible attendue
        target_distance = self.Pose2D(distance_x, distance_y, theta_rad)
        expected_end_position = init_position * target_distance

        # Activation ou non du mouvement des bras
        enable_arms = self.getParameter("Arms movement enabled")
        self.motion.setMoveArmsEnabled(enable_arms, enable_arms)

        # Commande de déplacement
        self.motion.moveTo(distance_x, distance_y, theta_rad)

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

    # Réveil et position initiale debout
    motion_service.wakeUp()
    posture_service.goToPosture("StandInit", 1.0)

    print("Robot prêt. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            motionAlert = 0.4
            left, right = SonarDetection(session,motionAlert)
            robotMouvement = RobotMovement(motion_service)
            pos2D = robotMouvement.Pose2D(x=0.5,y=0,theta=0)
            x,y,theta = pos2D.toVector()
            while left != -1 or right != -1 :
                if  left != -1 : theta += robotMouvement.modulo2PI(5.0)
                else : theta -= robotMouvement.modulo2PI(5.0)
                if -1.0 < theta < 1.0 : 
                    motion_service.moveToward(0.0, 0.0, theta, [["Frequency", 0.5]]) # TODO : voir pourquoi le robot tourne plus et marche plus
                    time.sleep(2)
                    left, right = SonarDetection(session,motionAlert)
                else : break
            if theta < -1  : theta = -1
            elif theta > 1 : theta = 1
            motion_service.moveToward(x, y, theta, [["Frequency", 0.5]])
            time.sleep(5)
    except Exception as e :
        raise e

