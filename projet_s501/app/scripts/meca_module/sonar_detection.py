import qi
import time 
def sonarDetection(session) :
    """
    résumé : interprétation de la détection du sonar
    paramètre :
        - session : session de connexion avec le robot
    """
    motion_service = session.service("ALMotion")
    position = session.service("ALRobotPosture")
    sonar_service = session.service("ALSonar")
    memory_service = session.service("ALMemory")

    # Subscribe to sonars, this will launch sonars (at hardware level)
    # and start data acquisition.
    sonar_service.subscribe("myApplication")

    # Now you can retrieve sonar data from ALMemory.
    # Get sonar left first echo (distance in meters to the first obstacle).
    motion_service.rest()

    time.sleep(2)

    position.goToPosture("StandInit", 1.0)

    time.sleep(1)
    for i in ["",1,2,3,4,5,6,7,8,9] :
        try :
            leftSensor = memory_service.getData(f"Device/SubDeviceList/US/Left/Sensor/Value{i}")

        # Same thing for right.
            rightSensor = memory_service.getData(f"Device/SubDeviceList/US/Right/Sensor/Value{i}")

            print(f"Value{i} left sensor {leftSensor} ; right sensor {rightSensor}")
        except Exception as e :
             continue

    # Unsubscribe from sonars, this will stop sonars (at hardware level)
    sonar_service.unsubscribe("myApplication")
