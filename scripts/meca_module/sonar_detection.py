import time 
from typing import Any
from ..utils.subricber import Subscriber, UnSubscriber

def SonarDetection(session : Any, meterAlert : int) -> tuple[int,int]:
    """
Interprétation de la détection du sonar.

Args:
    session: une session avec le robot
    meterAlert: distance à partir de laquelle on souhaite être alerté

Returns:
    un tuple de deux entier contenant la distance avec le robot -1 si rien n'est détecté
    """
    motion_service = session.service("ALMotion")
    position = session.service("ALRobotPosture")
    sonar_service = session.service("ALSonar")
    memory_service = session.service("ALMemory")

    Subscriber(session,"myApplication")

    # Important de le lever car le sonnar renverra des données que dans ce cas
    motion_service.rest()
    time.sleep(2)
    position.goToPosture("StandInit", 1.0)

    time.sleep(1) # laisser le temps au robot de lever
    try :
        leftSensor = memory_service.getData("Device/SubDeviceList/US/Left/Sensor/Value") # TODO : tester Value1 jusqu'à 9 pour voir si ces capteurs marchent
        rightSensor = memory_service.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        meterAlertValue = 0.4
        return (rightSensor if rightMeterTrak(meterAlert,rightSensor) else -1,leftSensor if leftMeterTrak(meterAlert,leftSensor) else -1 )

    except Exception as e :
        raise e

    UnSubscriber(session,"myApplication")

def rightMeterTrak(meterAlertValue : int, sensor : float) -> bool :
    """
S'assure que le robot n'atteint pas la distance donnée par meterAlertValue

Args:
    meterAlertValue: la distance avec un objet à ne pas atteindre
    rightSensor: donnée du sonar droit du robot
    
Returns:
    vrai si meterAlertValue est atteinte
    
    """
    return meterAlertValue >= rightSensor

def leftMeterTrak(meterAlertValue : int, sensor : float) -> bool :
    """
S'assure que le robot n'atteint pas la distance donnée par meterAlertValue

Args:
    meterAlertValue: la distance avec un objet à ne pas atteindre
    leftSensor: donnée du sonar gauche du robot
    
Returns:
    vrai si meterAlertValue est atteinte
    
    """
    return meterAlertValue >= leftSensor

if __name__ == '__main__' : pass