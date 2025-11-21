# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys

def main(session, args) :
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
        main(session, args)
    except RuntimeError:
        print(f"Impossible de se connecter à NAOqi à l'adresse {args.ip}:{args.port}.")
        sys.exit(1)
