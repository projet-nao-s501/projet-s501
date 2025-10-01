#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys
from projet_s501.app.scripts.meca_module.sonar_detection import sonarDetection 

from keras.models import load_model  # TensorFlow is required for Keras to work


def main(session):

    while True:
        sonarDetection(session)


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
    except RuntimeError as e:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    except KeyboardInterrupt :
        sys.exit(0)
    main(session)
