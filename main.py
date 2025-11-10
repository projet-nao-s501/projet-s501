#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Lien pour utiliser le flux video et entrainer un modele
# https://teachablemachine.withgoogle.com/

# Needed packages to use exported model
# pip install tensorflow==2.12.1 numpy==1.23.5 opencv-python==4.9.0.80

import qi
import argparse
import sys
import threading
import time
from scripts.utils.connexion_camera import connexionCamera
from scripts.ia_module.vocal.voice_recognition_2 import voice_recognition_2

def lancer_detection_couleur(session):
    """
    Lance le module de détection de 
    couleurs dans un thread séparé 
    """
    print("[Thread detection] Demarrage du module de detection de couleurs")
    try:
        connexionCamera(session)
    except Exception as e:
        print(f"[Thead detection] Erreur: {e}")

def lancer_reconnaissance_vocale(session):
    """
    Lance le module de reconnaissance
    vocale dans un thread séparé
    """
    print("[Thead vocal] Demarrage du module de reconnaissance vocale")
    try:
        voice_recognition_2(session)
    except Exception as e:
        print(f"[thead vocal] Erreur: {e}")
    

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
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    # Création des deux threads
    thread_detection = threading.Thread(target=lancer_detection_couleur, args=(session,))
    thread_vocal = threading.Thread(target=lancer_reconnaissance_vocale, args=(session,))

    # Démarrage des threads
    thread_detection.start()
    thread_vocal.start()

    print("[Main] Les deux modules sont lances")
    print("[Main] Appuyez sur 'q' dans la fenetre de detection pour arreter\n")

    # Attendre que les threads se terminent
    try:
        thread_detection.join()
        thread_vocal.join()
    except KeyboardInterrupt:
        print("\n[Main] Arret demande par l'utilisateur (Ctrl+C)")

    

