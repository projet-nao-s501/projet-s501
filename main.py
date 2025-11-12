#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Lien pour utiliser le flux video et entrainer un modele
# https://teachablemachine.withgoogle.com/

# Needed packages to use exported model
# pip install tensorflow==2.12.1 numpy==1.23.5 opencv-python==4.9.0.80

import qi
import argparse
import sys
import time
from scripts.utils.connexion_camera import connexionCamera
from typing import Any

def main(session : Any) :
    connexionCamera(session)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        main(session)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)