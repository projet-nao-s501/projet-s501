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
