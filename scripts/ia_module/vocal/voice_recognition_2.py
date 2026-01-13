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
    print("\nNettoyage des anciens abonnements ASR...")
    try:
        asr.unsubscribe("VoiceRecog_Sprint2")
        print("Desabonne: VoiceRecog_Sprint2")
    except:
        pass
    
    time.sleep(0.5)

    # Pause explicite du moteur ASR
    print("Mise en pause du moteur ASR...")
    try:
        asr.pause(True)
        time.sleep(2)
        print("Moteur ASR mis en pause")
    except Exception as e:
        print(f"Info pause: {e}")

    # Configuration ASR
    asr.setLanguage("French")
    print("Langue configuree: French")
    
    # Vocabulaire pour le Sprint 2
    vocabulary = ["couleur"]
    
    asr.setVocabulary(vocabulary, False)
    print(f"Vocabulaire charge: {', '.join(vocabulary)}")

    time.sleep(1)

    # Reprendre le moteur AVANT de s'abonner
    print("Reprise du moteur ASR...")
    try:
        asr.pause(False)
        time.sleep(1)
        print("Moteur ASR actif")
    except Exception as e:
        print(f"Info reprise: {e}")
    
    # Démarrage Reconnaissance
    asr.subscribe("VoiceRecog_Sprint2")
    print("Reconnaissance vocale activee")
    print("En attente du mot 'couleur'...\n")
    
    # Boucle d'écoute
    tts.setLanguage("French")
    last_word = ""
    iteration = 0
    max_iterations = 800  
    
    while iteration < max_iterations:
        time.sleep(0.1)
        iteration += 1
        
        #  Affichage progression toutes les 10 secondes
        if iteration % 100 == 0:
            print(f"[VOCAL] Ecoute active... {iteration//10}s", end="\r")
        
        # Récupérer le mot reconnu
        word_data = memory.getData("WordRecognized")
        
        if word_data and len(word_data) > 0:
            word = word_data[0]
            confidence = word_data[1]
            
            
            
            # Filtrer par confiance et éviter les répétitions
            if confidence > 0.4 and word != last_word:
                print(f"\n[Reconnu] Mot: '{word}' (confiance: {confidence*100:.0f}%)")
                
                if word == "couleur":
                    print("Traitement de la demande")
                    
                    # Lire la couleur depuis ALMemory
                    couleur = memory.getData("CouleurDetectee")
                    #couleur = couleur_detectee
                    
                    if couleur:
                        response = f"J'ai detecté du {couleur}"
                        print(f"Reponse: '{response}'")
                        tts.say(response)
                    else:
                        response = "Je n'ai detecte aucune couleur"
                        print(f"Reponse: '{response}'")
                        tts.say(response)
                    
                    last_word = word

                    # Reset pour permettre une nouvelle question
                    time.sleep(1)
                    last_word = ""
                else:
                    print(f"Pas de reponse pour: '{word}'")
    
    # Arrêt
    print("\n Arret du module vocal...")
    try:
        asr.unsubscribe("VoiceRecog_Sprint2")
        print("Reconnaissance vocale desactivee")
    except:
        pass
    
    try:
        asr.pause(True)
        print("Moteur ASR en pause")
    except:
        pass


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.163")
    parser.add_argument("--port", type=int, default=9559)
    
    args = parser.parse_args()
    
    # Connexion à NAO
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"\nConnecte a NAO sur {args.ip}:{args.port}\n")
    except RuntimeError:
        print(f"\nImpossible de se connecter a NAO sur {args.ip}:{args.port}")
        sys.exit(1)
    
    voice_recognition_2(session)