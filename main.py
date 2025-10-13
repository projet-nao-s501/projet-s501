# -*- encoding: UTF-8 -*-

"""
Script de contrôle de déplacement pour robot NAO.
Permet de commander le robot en déplacement avec gestion d'erreur de position.
Possibilité d'ajouter la capture vidéo et modèle IA (commenté pour l'instant).

Packages requis :
  pip install tensorflow==2.12.1 numpy==1.23.5 opencv-python==4.9.0.80
"""

import qi
import argparse
import sys
from scripts.meca_module.voice_recognition import test_text_to_speech, voice_recognition_sprint1  # TensorFlow is required for Keras to work
from scripts.meca_module.RobotMovement import marcheRobot

def main(session) :
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contrôle du robot NAO.")
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
    except RuntimeError:
        print(f"Impossible de se connecter à NAOqi à l'adresse {args.ip}:{args.port}.")
        sys.exit(1)
    if args.test:
        test_text_to_speech(session)
    else:
        voice_recognition_sprint1(session)
    marcheRobot(session)
