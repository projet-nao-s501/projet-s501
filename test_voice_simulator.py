#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Simulateur de test pour la reconnaissance vocale NAO - Sprint 1
Permet de tester la logique sans avoir le robot ou le simulateur NAOqi
"""

import time


class MockNAOSession:
    """Simule une session NAO pour les tests"""
    
    def __init__(self):
        self.services = {
            "ALSpeechRecognition": MockASR(),
            "ALMemory": MockMemory(),
            "ALTextToSpeech": MockTTS()
        }
    
    def service(self, service_name):
        return self.services.get(service_name)


class MockASR:
    """Simule le service ALSpeechRecognition"""
    
    def __init__(self):
        self.language = None
        self.vocabulary = []
        self.subscribed = False
    
    def setLanguage(self, language):
        self.language = language
        print(f"[MOCK ASR] Langue configurée: {language}")
    
    def setVocabulary(self, vocab, wordspotting):
        self.vocabulary = vocab
        print(f"[MOCK ASR] Vocabulaire: {vocab}")
    
    def subscribe(self, name):
        self.subscribed = True
        print(f"[MOCK ASR] Abonné: {name}")
    
    def unsubscribe(self, name):
        self.subscribed = False
        print(f"[MOCK ASR] Désabonné: {name}")


class MockMemory:
    """Simule le service ALMemory avec reconnaissance simulée"""
    
    def __init__(self):
        self.word_recognized = None
        self.simulation_sequence = [
            ("bonjour", 0.85),
            ("ça va", 0.72),
            ("projet", 0.68),
            ("merci", 0.90),
            ("moi", 0.75),
            ("au revoir", 0.88)
        ]
        self.current_step = 0
        self.last_call_time = time.time()
    
    def getData(self, key):
        if key == "WordRecognized":
            # Simuler un délai entre chaque mot reconnu (5 secondes)
            current_time = time.time()
            if current_time - self.last_call_time > 5 and self.current_step < len(self.simulation_sequence):
                word, confidence = self.simulation_sequence[self.current_step]
                self.current_step += 1
                self.last_call_time = current_time
                print(f"\n[MOCK MEMORY] Simulation: mot '{word}' reconnu")
                return [word, confidence]
            return None
        return None


class MockTTS:
    """Simule le service ALTextToSpeech"""
    
    def __init__(self):
        self.language = None
    
    def setLanguage(self, language):
        self.language = language
        print(f"[MOCK TTS] Langue TTS: {language}")
    
    def say(self, text):
        print(f"[MOCK TTS]  NAO dit: \"{text}\"")
        # Simuler le temps de parole (proportionnel à la longueur du texte)
        time.sleep(len(text) * 0.03)


def voice_recognition_sprint1(session):
    """
    Fonction de reconnaissance vocale (identique au code principal)
    """
    
    # Initialisation des services
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    print("=" * 60)
    print("RECONNAISSANCE VOCALE NAO - SPRINT 1 (MODE TEST)")
    print("=" * 60)
    
    # Configuration
    asr.setLanguage("French")
    print(" Langue configurée: Français")
    
    vocabulary = [
        "bonjour",
        "ça va",
        "projet", 
        "merci",
        "moi",
        "junior",
        "au revoir"
    ]
    
    asr.setVocabulary(vocabulary, False)
    print(f" Vocabulaire chargé: {', '.join(vocabulary)}")
    
    asr.subscribe("VoiceRecog_Sprint1")
    print(" Reconnaissance vocale activée")
    print("\n Le simulateur va automatiquement reconnaître les mots...\n")
    
    # Dictionnaire des réponses
    responses = {
        "bonjour": "Bonjour, j'espère que tu vas bien ?",
        "ça va": "Malgré quelques difficultés de la vie, ça va, je tiens le coup",
        "projet": "L'équipe composée de 10 membres doit me programmer afin que je puisse identifier un individu en fonction des caractéristiques qui me seront fournies. J'espère que j'ai été assez clair Junior ?",
        "merci": "Tu as encore besoin d'une information ?",
        "moi": "Lamaro Salif Junior, jeune homme portant des lunettes et qui se trouve actuellement trop proche de mon oreille. Peux-tu te décaler s'il te plait ?",
        "junior": "Lamaro Salif Junior, jeune homme portant des lunettes et qui se trouve actuellement trop proche de mon oreille. Peux-tu te décaler s'il te plait ?",
        "au revoir": "Bonne journée Junior"
    }
    
    # Boucle d'écoute
    conversation_active = True
    last_word = ""
    iteration = 0
    max_iterations = 120
    
    while conversation_active and iteration < max_iterations:
        time.sleep(0.5)
        iteration += 1
        
        # Récupérer le mot reconnu
        word_data = memory.getData("WordRecognized")
        
        if word_data and len(word_data) > 0:
            word = word_data[0]
            confidence = word_data[1]
            
            if confidence > 0.4 and word != last_word:
                print(f"\n Mot reconnu: '{word}' (confiance: {confidence*100:.0f}%)")
                
                if word in responses:
                    response = responses[word]
                    print(f" NAO répond:")
                    tts.say(response)
                    
                    if word == "au revoir":
                        print("\n Conversation terminée")
                        conversation_active = False
                    
                    last_word = word
    
    asr.unsubscribe("VoiceRecog_Sprint1")
    print("\n Reconnaissance vocale désactivée")
    print("=" * 60)


if __name__ == "__main__":
    print("\n MODE SIMULATEUR - Test sans robot NAO")
    print("Les mots seront automatiquement 'reconnus' toutes les 5 secondes")
    print("Séquence: bonjour → ça va → projet → merci → moi → au revoir\n")
    
    input("Appuyez sur ENTRÉE pour commencer le test...")
    
    # Créer une fausse session NAO
    mock_session = MockNAOSession()
    
    # Lancer la reconnaissance vocale avec le simulateur
    voice_recognition_sprint1(mock_session)
    
    print("\n Test terminé avec succès!")
    print("\n Prochaines étapes:")
    print("  1. Vérifier que la logique de conversation fonctionne")
    print("  2. Tester avec le vrai NAO/simulateur NAOqi quand disponible")
    print("  3. Ajuster les réponses si nécessaire")