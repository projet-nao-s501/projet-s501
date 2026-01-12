import qi
import time

def naoDanse(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    for _ in range(5):

        names = [
            "LHipRoll", "RHipRoll",             # Hanches
            "LShoulderRoll", "RShoulderRoll",   # Bras
            "LElbowRoll", "RElbowRoll"          # Coudes
        ]
        angles = [
            0.3, -0.3,      # Hanches
            0.6, -0.6,      # Bras (vers la gauche)
            -0.5, 0.5       # Coudes (légèrement pliés)
        ]
        motion.setAngles(names, angles, 0.3)
        time.sleep(0.5)

        angles = [
            -0.3, 0.3,      # Hanches
            -0.6, 0.6,      # Bras (vers la droite)
            0.5, -0.5       # Coudes (légèrement pliés)
        ]
        motion.setAngles(names, angles, 0.3)
        time.sleep(0.5)

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

