#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Lien pour utiliser le flux video et entrainer un modele
# https://teachablemachine.withgoogle.com/

# Needed packages to use exported model
# pip install tensorflow==2.12.1 numpy==1.23.5 opencv-python==4.9.0.80

import qi
from argparse import ArgumentParser, Namespace
import sys
from scripts.meca_module.voice_recognition import test_text_to_speech, voice_recognition_sprint1  # TensorFlow is required for Keras to work
from scripts.meca_module.RobotMovement import marcheRobot
import time
from scripts.utils.connexion_camera import connexionCamera
from scripts.meca_module.testSonardIeme import testTousLesCapteurs
from typing import Any

def main(session : Any, args : Namespace) -> None :
    """
    fonction principal de fonctionnement du robot
    
    Args:
        session: la session qui représente la connexion avec le robot
        args: les arguments passés lors de l'appel du fichier
    
    # """
    # if args.test:
    #     test_text_to_speech(session)
    # else:
    #     voice_recognition_sprint1(session)
    # connexionCamera(session)
    marcheRobot(session)
    # testTousLesCapteurs(session)
    

if __name__ == "__main__":
    parser = ArgumentParser(description="Contrôle du robot NAO.")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect(f"tcp://{args.ip}:{args.port}")
        main(session, args)
    except RuntimeError as e:
        if e.__str__().find("113") != -1 or e.__str__().find("111") != -1: print(f"Impossible de se connecter à l'adresse : {args.ip}:{args.port}")
        else : print(f"erreur survenu dans le robot : {e}") 
    except KeyboardInterrupt: print("Arrêt par l'utilisateur.")
    except Exception as e: print(f"erreur inattendu : {e}") 
    
    finally : sys.exit(1)
    
    
