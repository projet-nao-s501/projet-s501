#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Reconnaissance Vocale NAO - Sprint 1
Description: Conversation interactive en français avec NAO
"""

import time
import qi


def voice_recognition_sprint1(session):
    """
    Fonction principale de reconnaissance vocale pour le Sprint 1
    NAO reconnaît des mots-clés et répond de manière personnalisée
    """
    
    # Initialisation des services
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    try:
        print("Nettoyage des anciens abonnements ASR...")
        subscribers = asr.getSubscribersInfo()
        for subscriber in subscribers:
            try:
                asr.unsubscribe(subscriber)
                print(f"  Désabonné: {subscriber}")
            except Exception as e:
                print(f"  Impossible de désabonner {subscriber}: {e}")
    except Exception as e:
        print(f"Erreur lors du nettoyage: {e}")
    
    # PAUSE explicite du moteur ASR
    try:
        asr.pause(True)
        print("Moteur ASR mis en pause")
    except Exception as e:
        print(f"Info: {e}")

    print("RECONNAISSANCE VOCALE NAO - SPRINT 1")
    
    # Configuration de la langue en français
    asr.setLanguage("French")
    print(" Langue configurée: Français")
    
    # Définition du vocabulaire (mots-clés courts pour meilleure fiabilité)
    vocabulary = [
        "bonjour",
        "ça va",
        "projet", 
        "merci",
        "moi",
        "qui est junior ?",
        "au revoir"
    ]
    
    asr.setVocabulary(vocabulary, False)
    print(f" Vocabulaire chargé: {', '.join(vocabulary)}")
    
    # Démarrer la reconnaissance vocale
    asr.subscribe("VoiceRecog_Sprint1")
    print(" Reconnaissance vocale activée")
    print("\n NAO est à l'écoute... Parlez maintenant!\n")
    
    # Dictionnaire des réponses
    responses = {
        "bonjour": "Bonjour, j'espère que tu vas bien ?",
        "ça va": "Malgré quelques difficultés de la vie, ça va, je tiens le coup",
        "projet": "L'équipe composée de 10 membres doit me programmer afin que je puisse identifier un individu en fonction des caractéristiques qui me seront fournies. J'espère que j'ai été assez clair Junior ?",
        "merci": "Tu as encore besoin d'une information ?",
        "moi": "Lamaro Salif Junior, jeune homme portant des lunettes et qui se trouve actuellement trop proche de mon oreille. Peux-tu te décaler s'il te plait ?",
        "qui est junior ?": "Lamaro Salif Junior, jeune homme portant des lunettes et qui se trouve actuellement trop proche de mon oreille. Peux-tu te décaler s'il te plait ?",
        "au revoir": "Bonne journée Junior"
    }
    
    # Boucle d'écoute (60 secondes = 120 itérations x 0.5s)
    conversation_active = True
    last_word = ""
    iteration = 0
    max_iterations = 120
    
    while conversation_active and iteration < max_iterations:
        time.sleep(0.5)
        iteration += 1
        
        # Récupérer le mot reconnu depuis la mémoire de NAO
        word_data = memory.getData("WordRecognized")
        
        # Vérifier si un mot a été reconnu
        if word_data and len(word_data) > 0:
            word = word_data[0]
            confidence = word_data[1]
            
            # Filtrer les mots avec une confiance suffisante (> 40%)
            # Et éviter de répéter le même mot plusieurs fois
            if confidence > 0.4 and word != last_word:
                print(f"\n Mot reconnu: '{word}' (confiance: {confidence*100:.0f}%)")
                
                # Trouver et dire la réponse appropriée
                if word in responses:
                    response = responses[word]
                    print(f" NAO dit: \"{response}\"")
                    tts.say(response)
                    
                    # Si c'est "au revoir", terminer la conversation
                    if word == "au revoir":
                        print("\n Conversation terminée")
                        conversation_active = False
                    
                    last_word = word
                else:
                    print(f" Mot reconnu mais pas de réponse programmée pour: '{word}'")
    
    # Arrêter la reconnaissance vocale
    asr.unsubscribe("VoiceRecog_Sprint1")
    print("\n Reconnaissance vocale désactivée")
    print("=" * 60)


def test_text_to_speech(session):
    """
    Fonction de test simple pour vérifier que Text-to-Speech fonctionne
    """
    tts = session.service("ALTextToSpeech")
    tts.setLanguage("French")
    tts.say("Test de reconnaissance vocale, Sprint 1")
    print(" Test Text-to-Speech terminé")


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Adresse IP du robot NAO")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port NAOqi")
    parser.add_argument("--test", action="store_true",
                        help="Lancer uniquement le test TTS")
    
    args = parser.parse_args()
    
    # Connexion à NAO
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f" Connecté à NAO sur {args.ip}:{args.port}\n")
    except RuntimeError:
        print(f" Impossible de se connecter à NAO sur {args.ip}:{args.port}")
        print("Vérifiez que:")
        print("  - Le simulateur NAOqi est lancé (si en local)")
        print("  - L'adresse IP et le port sont corrects")
        sys.exit(1)
    
    # Lancer le test ou la reconnaissance vocale
    if args.test:
        test_text_to_speech(session)
    else:
        voice_recognition_sprint1(session)