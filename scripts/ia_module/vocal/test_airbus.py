#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import time
import qi

def test_airbus(session):
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    print("Test Airbus - Initialisation...")
    
    # Nettoyage
    try:
        asr.unsubscribe("TestAirbus")
    except:
        pass
    
    # Pause moteur ASR
    asr.pause(True)
    time.sleep(1)
    
    # Configuration
    asr.setLanguage("French")
    asr.setVocabulary(["airbus"], False)
    print("Vocabulaire charge: airbus")
    
    # Activation
    asr.subscribe("TestAirbus")
    tts.setLanguage("French")
    
    print("NAO ecoute... Dites 'airbus'\n")
    tts.say("Je t'ecoute")
    
    # Ecoute (30 secondes)
    for i in range(60):
        time.sleep(0.5)
        word_data = memory.getData("WordRecognized")
        
        if word_data and len(word_data) > 0:
            word = word_data[0]
            confidence = word_data[1]
            
            if confidence > 0.4 and word == "airbus":
                print(f"Mot reconnu: {word} ({confidence*100:.0f}%)")
                tts.say("Tu es le meilleur pilote junior")
                break
    
    asr.unsubscribe("TestAirbus")
    print("Test termine")

if __name__ == "__main__":
    import sys
    
    session = qi.Session()
    try:
        session.connect("tcp://172.16.1.163:9559")
        print("Connecte a NAO\n")
    except:
        print("Erreur de connexion")
        sys.exit(1)
    
    test_airbus(session)