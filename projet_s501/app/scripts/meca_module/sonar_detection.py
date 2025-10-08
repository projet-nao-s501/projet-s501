import time 
from typing import Any
from ..utils.subricber import Subriber

def SonarDetection(session : Any) -> None:
    """
Interprétation de la détection du sonar.

Args:
    session: une session avec le robot
    """
    motion_service = session.service("ALMotion")
    position = session.service("ALRobotPosture")
    sonar_service = session.service("ALSonar")
    memory_service = session.service("ALMemory")

    sonar_service.subscribe("myApplication")

    # Important de le lever car le sonnar renverra des données que dans ce cas
    motion_service.rest()
    time.sleep(2)
    position.goToPosture("StandInit", 1.0)

    time.sleep(1) # laisser le temps au robot de lever
    try :
        leftSensor = memory_service.getData("Device/SubDeviceList/US/Left/Sensor/Value") # TODO : tester Value1 jusqu'à 9 pour voir si ces capteurs marchent
        rightSensor = memory_service.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        meterAlertValue = 0.4
        isDepassed = meterTrak(meterAlertValue,rightSensor,leftSensor)
        
        if(isDepassed) :
            # TODO : la future fonction qui gèrera le dépassement de la frontière
            print(f"La frontiere de {meterAlertValue} est franchi")
            print(f"détection à gauche : {leftSensor}; détection à droite {rightSensor}")

    except Exception as e :
        print(e)
        return

    sonar_service.unsubscribe("myApplication")

def meterTrak(meterAlertValue : int, rightSensor : float, leftSensor : float) -> bool :
    """
S'assure que le robot n'atteint pas la distance donnée par meterAlertValue

Args:
    meterAlertValue: la distance avec un objet à ne pas atteindre
    rightSensor: donnée du sonar droit du robot
    leftSensor: donnée du sonar gauche du robot
    
Returns:
    vrai si meterAlertValue est atteinte
    
    """
    return meterAlertValue >= rightSensor and meterAlertValue >= leftSensor

if __name__ == '__main__' : pass