#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--port", type=int, default=9559)
    
    args = parser.parse_args()
    
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"Connecte a NAO sur {args.ip}:{args.port}")
    except RuntimeError as e:
        print(f"Erreur de connexion: {e}")
        sys.exit(1)
    
    from utils.connexion_camera import connexionCamera
    connexionCamera(session)