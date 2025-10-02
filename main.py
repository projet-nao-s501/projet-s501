#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys
from typing import Any
from projet_s501.app.scripts.meca_module.sonar_detection import SonarDetection, AUnObjetDansSonChamp

def main(session : Any) -> None:
    """
Fonction principal du paquage

Args:
    session: La session en cours avec le robot
    """

    while True:
        SonarDetection(session) ## votre fonction ici
        aRienDansSonChamp = AUnObjetDansSonChamp(session)
        if(not(aRienDansSonChamp)) : print("le champ est libre")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.163",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError as e:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    except KeyboardInterrupt :
        sys.exit(0)
    main(session)
