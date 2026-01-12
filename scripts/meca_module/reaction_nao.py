import qi
import time
import almath

# def naoDanse(session):
#     motion = session.service("ALMotion")
#     posture = session.service("ALRobotPosture")

#     motion.wakeUp()
#     posture.goToPosture("StandInit", 0.5)

#     # Paramètres pour la danse
#     for _ in range(5):

#         # Étape 1 : Hanche gauche + bras gauche haut / bras droit bas
#         names = [
#             "LHipRoll", "RHipRoll",
#             "LShoulderPitch", "RShoulderPitch",
#             "LShoulderRoll", "RShoulderRoll",
#             "LElbowRoll", "RElbowRoll",
#             "HeadYaw", "HeadPitch"
#         ]
#         angles = [
#             0.2, -0.2,       # Hanches
#             0.5, 0.2,        # Bras (gauche haut, droit bas)
#             0.3, -0.3,       # Épaules latérales
#             -0.5, 0.5,       # Coudes pliés
#             0.0, 0.1         # Tête légèrement droite
#         ]
#         motion.setAngles(names, angles, 0.3)
#         time.sleep(0.5)

#         # Étape 2 : Hanche droite + bras droit haut / bras gauche bas
#         angles = [
#             -0.2, 0.2,       # Hanches
#             0.2, 0.5,        # Bras (droite haut, gauche bas)
#             -0.3, 0.3,       # Épaules latérales
#             0.5, -0.5,       # Coudes pliés
#             0.0, -0.1        # Tête légèrement gauche
#         ]
#         motion.setAngles(names, angles, 0.3)
#         time.sleep(0.5)

#         # Étape 3 : Hanche centrale + bras en mouvement intermédiaire
#         angles = [
#             0.0, 0.0,
#             0.3, 0.3,
#             0.0, 0.0,
#             0.0, 0.0,
#             0.0, 0.0
#         ]
#         motion.setAngles(names, angles, 0.3)
#         time.sleep(0.3)

#     # Retour à posture initiale
#     posture.goToPosture("StandInit", 0.5)

def naoDanse(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")

    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

     # Enable Whole Body Balancer
    isEnabled  = True
    motion.wbEnable(isEnabled)

    # Legs are constrained fixed
    stateName  = "Fixed"
    supportLeg = "Legs"
    motion.wbFootState(stateName, supportLeg)

    # Constraint Balance Motion
    isEnable   = True
    supportLeg = "Legs"
    motion.wbEnableBalanceConstraint(isEnable, supportLeg)

    useSensorValues = False

    # Arms motion
    effectorList = ["LArm", "RArm"]

    frame = motion.FRAME_ROBOT

    # pathLArm
    pathLArm = []
    currentTf = motion.getTransform("LArm", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += 0.08 # y
    target1Tf.r3_c4 += 0.14 # z

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= 0.05 # y
    target2Tf.r3_c4 -= 0.07 # z

    pathLArm.append(list(target1Tf.toVector()))
    pathLArm.append(list(target2Tf.toVector()))
    pathLArm.append(list(target1Tf.toVector()))
    pathLArm.append(list(target2Tf.toVector()))
    pathLArm.append(list(target1Tf.toVector()))

    # pathRArm
    pathRArm = []
    currentTf = motion.getTransform("RArm", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += 0.05 # y
    target1Tf.r3_c4 -= 0.07 # z

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= 0.08 # y
    target2Tf.r3_c4 += 0.14 # z

    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))
    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))
    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))

    pathList = [pathLArm, pathRArm]

    axisMaskList = [almath.AXIS_MASK_VEL, # for "LArm"
                    almath.AXIS_MASK_VEL] # for "RArm"

    coef       = 1.5
    timesList  = [ [coef*(i+1) for i in range(5)],  # for "LArm" in seconds
                   [coef*(i+1) for i in range(6)] ] # for "RArm" in seconds

    # called cartesian interpolation
    motion.transformInterpolations(effectorList, frame, pathList, axisMaskList, timesList)

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

# Torso Motion
    effectorList = ["Torso", "LArm", "RArm"]

    dy = 0.06
    dz = 0.06

    # pathTorso
    currentTf = motion.getTransform("Torso", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += dy
    target1Tf.r3_c4 -= dz

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= dy
    target2Tf.r3_c4 -= dz

    pathTorso = []
    for i in range(3):
        pathTorso.append(list(target1Tf.toVector()))
        pathTorso.append(currentTf)
        pathTorso.append(list(target2Tf.toVector()))
        pathTorso.append(currentTf)

    pathLArm = [motion.getTransform("LArm", frame, useSensorValues)]
    pathRArm = [motion.getTransform("RArm", frame, useSensorValues)]

    pathList = [pathTorso, pathLArm, pathRArm]

    axisMaskList = [almath.AXIS_MASK_ALL, # for "Torso"
                    almath.AXIS_MASK_VEL, # for "LArm"
                    almath.AXIS_MASK_VEL] # for "RArm"

    coef       = 0.5
    timesList  = [
                  [coef*(i+1) for i in range(12)], # for "Torso" in seconds
                  [coef*12],                       # for "LArm" in seconds
                  [coef*12]                        # for "RArm" in seconds
                 ]

    motion.transformInterpolations(
        effectorList, frame, pathList, axisMaskList, timesList)
    
    # Deactivate whole body
    isEnabled    = False
    motion.wbEnable(isEnabled)

    # Send robot to Pose Init
    posture.goToPosture("StandInit", 0.3)

    # Go to rest position
    motion.rest()

