import qi
import time

def naoDanse(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    # Paramètres pour la danse
    for _ in range(5):

        # Étape 1 : Hanche gauche + bras gauche haut / bras droit bas
        names = [
            "LHipRoll", "RHipRoll",
            "LShoulderPitch", "RShoulderPitch",
            "LShoulderRoll", "RShoulderRoll",
            "LElbowRoll", "RElbowRoll",
            "HeadYaw", "HeadPitch"
        ]
        angles = [
            0.2, -0.2,       # Hanches
            0.5, 0.2,        # Bras (gauche haut, droit bas)
            0.3, -0.3,       # Épaules latérales
            -0.5, 0.5,       # Coudes pliés
            0.0, 0.1         # Tête légèrement droite
        ]
        motion.setAngles(names, angles, 0.3)
        time.sleep(0.5)

        # Étape 2 : Hanche droite + bras droit haut / bras gauche bas
        angles = [
            -0.2, 0.2,       # Hanches
            0.2, 0.5,        # Bras (droite haut, gauche bas)
            -0.3, 0.3,       # Épaules latérales
            0.5, -0.5,       # Coudes pliés
            0.0, -0.1        # Tête légèrement gauche
        ]
        motion.setAngles(names, angles, 0.3)
        time.sleep(0.5)

        # Étape 3 : Hanche centrale + bras en mouvement intermédiaire
        angles = [
            0.0, 0.0,
            0.3, 0.3,
            0.0, 0.0,
            0.0, 0.0,
            0.0, 0.0
        ]
        motion.setAngles(names, angles, 0.3)
        time.sleep(0.3)

    # Retour à posture initiale
    posture.goToPosture("StandInit", 0.5)


def naoDab(session):

    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)
    
    names = [
        "RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowRoll",
        "HeadYaw", "HeadPitch"
    ]

    angles = [
        -0.5,  0.0,  1.5, -0.5,    # Bras droit plié devant la tête vers la gauche
        -0.2,   0.8,  0.0,     # Bras gauche tendu vers la gauche
        -0.6, -0.4             # Tête tournée et inclinée vers la droite
    ]

    motion.setAngles(names, angles, 0.4)
    time.sleep(1)

    names = [
        "LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LElbowYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowRoll",
        "HeadYaw", "HeadPitch"
    ]

    angles = [
        0.5, 0.0, -1.5, 0.5,  # Bras gauche plié devant la tête vers la droite
        0.2, -0.8,  0.0,       # Bras droit tendu vers la droite
        0.6, 0.4               # Tête tournée et inclinée vers la gauche
    ]

    motion.setAngles(names, angles, 0.4)

    posture.goToPosture("StandInit", 0.5)

