import qi

def sonarDetection(session) :
    """
    résumé : interprétation de la détection du sonar
    paramètre :
        - session : session de connexion avec le robot
    """
    motion_service  = session.service("ALMotion")

    memory_service = session.service("ALMemory")
    sonar_service = session.service("ALSonar")

    # Subscribe to sonars, this will launch sonars (at hardware level)
    # and start data acquisition.
    sonar_service.subscribe("myApplication")

    # Now you can retrieve sonar data from ALMemory.
    # Get sonar left first echo (distance in meters to the first obstacle).
    for i in ["",1,2,3,4,5,6,7,8,9] :
        try :
            leftSensor = memory_service.getData(f"Device/SubDeviceList/US/Left/Sensor/Value{i}")

        # Same thing for right.
            rightSensor = memory_service.getData(f"Device/SubDeviceList/US/Right/Sensor/Value{i}")

            print(f"Value{i} left sensor {leftSensor} ; right sensor {rightSensor}")
        except :
            continue

    # Unsubscribe from sonars, this will stop sonars (at hardware level)
    sonar_service.unsubscribe("myApplication")
