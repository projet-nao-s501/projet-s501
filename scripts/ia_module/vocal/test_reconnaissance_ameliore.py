#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import time

def activer_microphones(session):
    """
    Active et configure correctement les microphones de NAO
    """
    print("\n=== ACTIVATION DES MICROPHONES ===")
    
    try:
        audio = session.service("ALAudioDevice")
        
        # Méthode 1 : Activer l'entrée audio
        print("Tentative d'activation de l'entrée audio...")
        try:
            audio.setOutputVolume(80)
            print("✓ Volume de sortie configuré")
        except Exception as e:
            print(f"Info volume sortie: {e}")
        
        # Méthode 2 : Vérifier l'état des microphones
        try:
            audio.enableAllMicrophones()
            print("✓ Microphones activés via enableAllMicrophones()")
        except AttributeError:
            print("⚠️ enableAllMicrophones() n'existe pas sur ce robot")
        except Exception as e:
            print(f"Info activation micros: {e}")
        
        # Méthode 3 : Configurer le front microphone
        try:
            audio.setParameter("Audio/MicSelectMode", 0)
            print("✓ Microphones avant sélectionnés")
        except Exception as e:
            print(f"Info sélection micros: {e}")
            
    except Exception as e:
        print(f"Erreur générale: {e}")
    
    print("=== FIN ACTIVATION ===\n")
    time.sleep(1)


def test_reconnaissance_ameliore(session):
    """
    Test de reconnaissance avec configuration améliorée
    """
    print("=== TEST RECONNAISSANCE AMÉLIORÉ ===\n")
    
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    try:
        # 1. Nettoyage complet - DÉSABONNER TOUT
        print("1. Nettoyage des abonnements...")
        try:
            subscribers = asr.getSubscribersInfo()
            for sub in subscribers:
                try:
                    asr.unsubscribe(sub)
                    print(f"   Désabonné: {sub}")
                except:
                    pass
        except:
            pass
        
        time.sleep(0.5)
        
        # 2. PAUSE COMPLÈTE du moteur - CRITIQUE !
        print("2. Mise en pause COMPLÈTE du moteur ASR...")
        try:
            asr.pause(True)
            time.sleep(2)  # Attendre que la pause soit effective
            print("   ✓ Moteur mis en pause")
        except Exception as e:
            print(f"   Info pause: {e}")
        
        # 3. Configuration langue et vocabulaire PENDANT LA PAUSE
        print("3. Configuration du vocabulaire (moteur en pause)...")
        try:
            asr.setLanguage("French")
            print("   ✓ Langue: Français")
            
            # Vocabulaire très simple
            vocabulary = ["oui", "non", "test"]
            asr.setVocabulary(vocabulary, False)
            print(f"   ✓ Vocabulaire configuré: {vocabulary}")
        except Exception as e:
            print(f"   ❌ Erreur configuration vocabulaire: {e}")
            return
        
        # 4. Configuration sensibilité (pendant la pause)
        print("4. Configuration de la sensibilité...")
        try:
            asr.setAudioExpression(True)
            print("   ✓ Expression audio activée")
        except Exception as e:
            print(f"   Info: {e}")
        
        time.sleep(1)
        
        # 5. REPRENDRE le moteur ASR
        print("5. Reprise du moteur ASR...")
        try:
            asr.pause(False)
            time.sleep(1)
            print("   ✓ Moteur ASR actif")
        except Exception as e:
            print(f"   Info: {e}")
        
        # 6. S'abonner APRÈS avoir tout configuré
        print("6. Activation de l'écoute...\n")
        asr.subscribe("TestReconnaissance")
        time.sleep(0.5)
        
        # Message vocal pour indiquer que c'est prêt
        tts.setLanguage("French")
        tts.say("Je suis prêt. Dis test.")
        
        print("=" * 60)
        print("🎤 NAO ÉCOUTE - Dites 'test', 'oui' ou 'non'")
        print("   Parlez FORT et LENTEMENT")
        print("   Approchez-vous des microphones (tête de NAO)")
        print("=" * 60 + "\n")
        
        # Écoute prolongée avec feedback visuel
        heard_something = False
        for i in range(40):  # 20 secondes
            time.sleep(0.5)
            
            # Afficher un point toutes les 2 secondes pour montrer que ça tourne
            if i % 4 == 0:
                print(f"   Écoute... {i//4}s", end="\r")
            
            word_data = memory.getData("WordRecognized")
            
            if word_data and len(word_data) > 0:
                word = word_data[0]
                confidence = word_data[1]
                
                # Afficher TOUS les résultats, même faible confiance
                if confidence > 0.1:  # Seuil très bas pour debug
                    print(f"\n   🔊 Détecté: '{word}' (confiance: {confidence*100:.1f}%)")
                    
                    if confidence > 0.3:
                        print(f"   ✅ MOT RECONNU AVEC SUCCÈS!")
                        tts.say(f"J'ai entendu {word}")
                        heard_something = True
                        break
        
        print("\n")
        
        # Désabonner proprement
        try:
            asr.unsubscribe("TestReconnaissance")
            print("   Écoute désactivée")
        except:
            pass
        
        if not heard_something:
            print("❌ AUCUN MOT RECONNU")
            print("\n🔍 Causes possibles:")
            print("   1. Microphones physiquement défectueux")
            print("   2. Volume ambiant trop élevé")
            print("   3. Vous êtes trop loin du robot")
            print("   4. Vous ne parlez pas assez fort")
            print("\n💡 Essayez:")
            print("   - Placez-vous à 20-30 cm de la tête de NAO")
            print("   - Parlez TRÈS FORT")
            print("   - Articulez: 'TESSST' lentement")
        else:
            print("✅ TEST RÉUSSI - Les microphones fonctionnent!")
            print("   → Vous pouvez maintenant corriger votre script Sprint 1")
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Nettoyage final
        try:
            asr.pause(True)
        except:
            pass


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
        print(f"✓ Connecté à NAO sur {args.ip}:{args.port}\n")
    except RuntimeError:
        print(f"✗ Impossible de se connecter à {args.ip}:{args.port}")
        sys.exit(1)
    
    # Étape 1 : Activer les microphones
    activer_microphones(session)
    
    # Étape 2 : Test de reconnaissance
    test_reconnaissance_ameliore(session)