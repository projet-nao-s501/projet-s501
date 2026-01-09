#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
###
"""
 Module vocal pour répondre aux 
 questions sur les couleurs 
 détectées
"""

import time
import qi

def voice_recognition_2(session, couleur_detectee):
    """
    - Écoute la question "Quelle couleur ?"
    - Lit la couleur détectée dans ALMemory 
    (stockée par connexionCamera)
    - Répond vocalement 
    "J'ai détecté du [couleur]"
    """
    
    # Initialisation des services
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    # Nettoyage des anciens abonnements
    try:
        print("\n Nettoyage des anciens abonnements ASR...")
        subscribers = asr.getSubscribersInfo()
        for subscriber in subscribers:
            try:
                asr.unsubscribe(subscriber)
                print(f"Desabonne: {subscriber}")
            except Exception as e:
                print(f"Impossible de desabonner {subscriber}: {e}")
    except Exception as e:
        print(f"Erreur lors du nettoyage: {e}")
    
    # Pause explicite du moteur ASR
    try:
        asr.pause(True)
        print("Moteur ASR mis en pause")
    except Exception as e:
        print(f"{e}")

    # Configuration ASR
    asr.setLanguage("French")
    print("Langue configuree: French")
    
    # Vocabulaire pour le Sprint 2
    vocabulary = [
        "couleur"
    ]
    
    asr.setVocabulary(vocabulary, False)
    print(f"Vocabulaire charge: {', '.join(vocabulary)}")
    
    # Démarrage Reconnaissance
    asr.subscribe("VoiceRecog_Sprint2")
    print("Reconnaissance vocale activee")
    
    # Boucle d'écoute
    tts.setLanguage("French")
    last_word = ""
    iteration = 0
    max_iterations = 200  # Environ 100 secondes (200 x 0.5s)
    
    while iteration < max_iterations:
        time.sleep(0.5)
        iteration += 1
        
        # Récupérer le mot reconnu
        word_data = memory.getData("WordRecognized")
        
        if word_data and len(word_data) > 0:
            word = word_data[0]
            confidence = word_data[1]
            
            # Filtrer par confiance et éviter les répétitions
            if confidence > 0.4 and word != last_word:
                print(f"\n[Reconnu] Mot: '{word}' (confiance: {confidence*100:.0f}%)")
                
                if word == "couleur":
                    print("I hear the word color")
                    # Lire la couleur depuis ALMemory
                    # couleur = memory.getData("CouleurDetectee")
                    couleur = couleur_detectee
                    
                    if couleur:
                        response = f"J'ai detecté du {couleur}"
                        print(f"[Response] NAO say: '{response}'")
                        tts.say(response)
                    else:
                        response = "Je n'ai pas detecté une couleur"
                        print(f"[Response] NAO say: '{response}'")
                        tts.say(response)
                    
                    last_word = word
                else:
                    print(f"[Info] Mot reconnu mais pas de reponse programmee pour: '{word}'")
    
    # Arrêt
    asr.unsubscribe("voice_recognition_2")
    print("\n[Fin]Reconnaissance vocale desactivee")


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.164",
                        help="Adresse IP du robot NAO")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi")
    
    args = parser.parse_args()
    
    # Connexion à NAO
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"\nConnecte a NAO sur {args.ip}:{args.port}\n")
    except RuntimeError:
        print(f"\nImpossible de se connecter a NAO sur {args.ip}:{args.port}")
        print("Verifiez que:")
        print("  - Le simulateur NAOqi est lance (si en local)")
        print("  - L'adresse IP et le port sont corrects")
        sys.exit(1)
    
    voice_recognition_2(session)