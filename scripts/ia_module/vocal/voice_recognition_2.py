#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
 Module vocal pour répondre aux 
 questions sur les couleurs 
 détectées
"""

import time
import qi

def voice_recognition_2(session):
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
        print("\n[INIT] Nettoyage des anciens abonnements ASR...")
        subscribers = asr.getSubscribersInfo()
        for subscriber in subscribers:
            try:
                asr.unsubscribe(subscriber)
                print(f"  Desabonne: {subscriber}")
            except Exception as e:
                print(f"  Impossible de desabonner {subscriber}: {e}")
    except Exception as e:
        print(f"[WARN] Erreur lors du nettoyage: {e}")
    
    # Pause explicite du moteur ASR
    try:
        asr.pause(True)
        print("[INIT] Moteur ASR mis en pause")
    except Exception as e:
        print(f"[INFO] {e}")

    # Configuration ASR
    asr.setLanguage("English")
    print("[CONFIG] Langue configuree: English")
    
    # Vocabulaire pour le Sprint 2
    vocabulary = [
        "color"
    ]
    
    asr.setVocabulary(vocabulary, False)
    print(f"[CONFIG] Vocabulaire charge: {', '.join(vocabulary)}")
    
    # Démarrage Reconnaissance
    asr.subscribe("VoiceRecog_Sprint2")
    print("[ACTIF] Reconnaissance vocale activee")
    print("\n[INFO] NAO est a l'ecoute. Demandez 'Quelle couleur ?'\n")
    
    # Boucle d'écoute
    tts.setLanguage("English")
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
                print(f"\n[RECONNU] Mot: '{word}' (confiance: {confidence*100:.0f}%)")
                
                if word == "color":
                    # Lire la couleur depuis ALMemory
                    couleur = memory.getData("CouleurDetectee")
                    
                    if couleur:
                        response = f"I detected {couleur}"
                        print(f"[RESPONSE] NAO say: '{response}'")
                        tts.say(response)
                    else:
                        response = "I did not detect any color"
                        print(f"[RESPONSE] NAO say: '{response}'")
                        tts.say(response)
                    
                    last_word = word
                else:
                    print(f"[INFO] Mot reconnu mais pas de reponse programmee pour: '{word}'")
    
    # Arrêt
    asr.unsubscribe("VoiceRecog_Sprint2")
    print("\n[FIN] Reconnaissance vocale desactivee")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Adresse IP du robot NAO")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi")
    
    args = parser.parse_args()
    
    # Connexion à NAO
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"\n[CONNEXION] Connecte a NAO sur {args.ip}:{args.port}\n")
    except RuntimeError:
        print(f"\n[ERREUR] Impossible de se connecter a NAO sur {args.ip}:{args.port}")
        print("Verifiez que:")
        print("  - Le simulateur NAOqi est lance (si en local)")
        print("  - L'adresse IP et le port sont corrects")
        sys.exit(1)
    
    voice_recognition_2(session)