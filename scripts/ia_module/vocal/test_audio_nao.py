#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import time

def diagnostic_complet(session):
    """
    Diagnostic complet du système audio de NAO
    """
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLET SYSTÈME AUDIO NAO")
    print("="*60 + "\n")
    
    # 1. Test Text-to-Speech
    print("1. TEST TEXT-TO-SPEECH")
    try:
        tts = session.service("ALTextToSpeech")
        tts.setLanguage("French")
        tts.say("Test de sortie audio")
        print("   ✓ Text-to-Speech fonctionne\n")
    except Exception as e:
        print(f"   ✗ Erreur TTS: {e}\n")
        return
    
    # 2. Test Audio Device
    print("2. TEST PÉRIPHÉRIQUE AUDIO")
    try:
        audio = session.service("ALAudioDevice")
        input_vol = audio.getParameter("inputVolume")
        output_vol = audio.getParameter("outputVolume")
        print(f"   Volume entrée: {input_vol}%")
        print(f"   Volume sortie: {output_vol}%")
        
        if input_vol < 50:
            audio.setParameter("inputVolume", 80)
            print("   → Volume d'entrée augmenté à 80%")
        print("   ✓ Périphérique audio OK\n")
    except Exception as e:
        print(f"   ✗ Erreur audio device: {e}\n")
    
    # 3. Test Speech Recognition
    print("3. TEST RECONNAISSANCE VOCALE")
    try:
        asr = session.service("ALSpeechRecognition")
        memory = session.service("ALMemory")
        
        # Nettoyage
        subscribers = asr.getSubscribersInfo()
        for sub in subscribers:
            try:
                asr.unsubscribe(sub)
            except:
                pass
        
        # Configuration
        asr.setLanguage("French")
        asr.setVocabulary(["test", "bonjour"], False)
        asr.subscribe("DiagnosticTest")
        
        print("   Reconnaissance vocale activée")
        print("   Dites 'test' ou 'bonjour' maintenant...")
        print("   (Attente de 10 secondes)")
        
        # Écoute
        heard_something = False
        for i in range(20):
            time.sleep(0.5)
            word_data = memory.getData("WordRecognized")
            if word_data and len(word_data) > 0:
                word = word_data[0]
                confidence = word_data[1]
                if confidence > 0.3:
                    print(f"   ✓ MOT RECONNU: '{word}' ({confidence*100:.0f}%)")
                    heard_something = True
                    break
        
        asr.unsubscribe("DiagnosticTest")
        
        if not heard_something:
            print("   ✗ AUCUN MOT RECONNU")
            print("   → Problème probable avec les microphones")
        
        print()
    except Exception as e:
        print(f"   ✗ Erreur ASR: {e}\n")
    
    print("="*60)
    print("FIN DU DIAGNOSTIC")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.163")
    parser.add_argument("--port", type=int, default=9559)
    args = parser.parse_args()
    
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print(f"✓ Connecté à NAO sur {args.ip}:{args.port}")
    except RuntimeError:
        print(f"✗ Impossible de se connecter à {args.ip}:{args.port}")
        sys.exit(1)
    
    diagnostic_complet(session)