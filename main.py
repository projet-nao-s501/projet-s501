# -*- encoding: UTF-8 -*-

import qi
from argparse import ArgumentParser, Namespace
import sys
from scripts.meca_module.voice_recognition import test_text_to_speech, voice_recognition_sprint1  # TensorFlow is required for Keras to work
from scripts.meca_module.RobotMovement import marcheRobot
from typing import Any

def main(session : Any, args : Namespace) -> None :
    """
    fonction principal de fonctionnement du robot
    
    Args:
        session: la session qui représente la connexion avec le robot
        args: les arguments passés lors de l'appel du fichier
    
    """
    if args.test:
        test_text_to_speech(session)
    else:
        voice_recognition_sprint1(session)
    marcheRobot(session)

if __name__ == "__main__":
    parser = ArgumentParser(description="Contrôle du robot NAO.")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Adresse IP du robot NAO (ex: 192.168.x.x)")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi (par défaut: 9559)")
    parser.add_argument("--test", action="store_true",
                        help="Lancer uniquement le test TTS")

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
    
    
