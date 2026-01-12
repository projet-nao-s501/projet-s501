import qi
import time
import numpy as np
from spatialmath import SE3

def offset_tf(original_tf, x_off=0.0, y_off=0.0, z_off=0.0):
    new_tf = list(original_tf)
    new_tf[3]  += x_off
    new_tf[7]  += y_off
    new_tf[11] += z_off
    return new_tf

def naoDanse(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    motion.wbEnable(True)
    motion.wbFootState("Fixed", "Legs")
    motion.wbEnableBalanceConstraint(True, "Legs")

    useSensorValues = False
    frame = 2 
    effectorList = ["LArm", "RArm"]

    current_tf_l = motion.getTransform("LArm", frame, useSensorValues)
    
    target1_l = offset_tf(current_tf_l, y_off=0.08, z_off=0.14)

    target2_l = offset_tf(current_tf_l, y_off=-0.05, z_off=-0.07)

    pathLArm = [target1_l, target2_l, target1_l, target2_l, target1_l]

    current_tf_r = motion.getTransform("RArm", frame, useSensorValues)
    
    target1_r = offset_tf(current_tf_r, y_off=0.05, z_off=-0.07)

    target2_r = offset_tf(current_tf_r, y_off=-0.08, z_off=0.14)

    pathRArm = [target1_r, target2_r, target1_r, target2_r, target1_r, target2_r]

    pathList = [pathLArm, pathRArm]
    axisMaskList = [63, 63]

    coef = 1.5
    timesList = [
        [coef * (i + 1) for i in range(5)], 
        [coef * (i + 1) for i in range(6)]
    ]

    motion.transformInterpolations(effectorList, frame, pathList, axisMaskList, timesList)

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


import time

import qi
import time

def sad(session):

    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")
    tts = session.service("ALTextToSpeech")

    motion.wakeUp()

    posture.goToPosture("Sit", 0.5)
    time.sleep(1)

    names = [
        "HeadPitch",
        "LKneePitch", "RKneePitch", 
        "LAnklePitch", "RAnklePitch"
    ]

    angles = [
        0.65,         # Tête plus baissée
        0.2, 0.2,     # Légère flexion des genoux
        -0.05, -0.05  # Légère compensation chevilles
    ]

    motion.setAngles(names, angles, 0.2)
    time.sleep(0.5)

    tts.say("Ouin ouin, j'ai pas trouvé.")


def checker(session):

    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")
    tts = session.service("ALTextToSpeech")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.6)
    time.sleep(0.5)

    names = [
        "RShoulderPitch",
        "RShoulderRoll",
        "RElbowYaw",
        "RElbowRoll"
    ]

    angles = [
        -0.5,   # Bras en avant
        -0.3,   # Ouvert sur le côté
        1.4,    # Orientation coude
        0.5     # Bras légèrement plié
    ]

    motion.setAngles(names, angles, 0.4)
    time.sleep(0.8)

    motion.openHand("RHand")
    time.sleep(0.4)
    motion.closeHand("RHand")

    tts.say("Salut, ça va ? Checke-moi ça !")

    posture.goToPosture("StandInit", 0.5)




