import qi
import time

def naoDanse(session):

    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    for _ in range(3):

        names = [
            "LHipRoll", "RHipRoll",
            "LShoulderRoll", "RShoulderRoll"
        ]

        angles = [
            0.3, -0.3,
            0.4, 0.2
        ]

        motion.setAngles(names, angles, 0.3)
        time.sleep(0.5)

        angles = [
            -0.3, 0.3,
            0.2, 0.4
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
        "RShoulderPitch", "RShoulderRoll", "RElbowRoll",
        "LShoulderPitch", "LShoulderRoll", "LElbowRoll",
        "HeadYaw", "HeadPitch"
    ]

    angles = [
        -0.4, -0.3, 1.0,     # Bras droit (plié, horizontal)
        1.2,  0.6, -0.6,     # Bras gauche (vers le bas)
        0.6,  0.4            # Tête tournée vers la gauche
    ]

    motion.setAngles(names, angles, 0.4)
    time.sleep(1)
    posture.goToPosture("StandInit", 0.5)

