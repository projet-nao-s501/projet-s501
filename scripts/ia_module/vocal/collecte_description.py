# -*- coding: utf-8 -*-
"""
Script de collecte de description pour recherche de personne - NAO Robot
Utilise une approche vocale guidée par étapes pour maximiser la fiabilité
Auteur: Junior - Équipe IA
Date: Janvier 2026
"""

import sys
import time
import qi
import argparse

# ============================================
# CONFIGURATION
# ============================================

# Paramètres de connexion au robot
DEFAULT_ROBOT_IP = "172.16.1.163"  
DEFAULT_ROBOT_PORT = 9559

# Timeouts et tentatives pour chaque phase
TIMEOUT_ECOUTE = 10  # Durée d'écoute par tentative en secondes
MAX_TENTATIVES = 3   # Nombre maximum de tentatives par phase

# Seuil de confiance pour la reconnaissance vocale (0.0 à 1.0)
SEUIL_CONFIANCE = 0.25  # ABAISSÉ de 0.35 à 0.25

# Vocabulaire : Phrases de déclenchement (Phase 1)
PHRASES_DECLENCHEMENT = [
    "trouve",
    "cherche"
]

# Vocabulaire : Types de vêtements
VETEMENTS_HAUT = [
    "chemise",
    "pull",
    "veste",
    "polo",
]

VETEMENTS_BAS = [
    "pantalon",
    "jupe"
]

# Vocabulaire : Couleurs
COULEURS = [
    "rouge",
    "bleu",
    "vert",
    "noir",
    "blanc",
    "jaune",
    "rose",
]

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def cleanup_services(asr, memory):
    """
    Nettoie proprement tous les services ASR et ALMemory avant de commencer
    """
    print("[CLEANUP] Nettoyage des services existants...")
    
    try:
        if asr:
            try:
                asr.unsubscribe("collecte_description")
                print("[CLEANUP] Service ASR désabonné")
            except:
                pass
            
            try:
                asr.pause(True)
                print("[CLEANUP] Service ASR mis en pause")
            except:
                pass
        
        if memory:
            try:
                memory.removeData("recherche_config")
                print("[CLEANUP] Données ALMemory nettoyées")
            except:
                pass
            
            # NOUVEAU : Vider aussi WordRecognized au cleanup
            try:
                memory.insertData("WordRecognized", [])
                print("[CLEANUP] WordRecognized vidé")
            except:
                pass
        
        print("[CLEANUP] Nettoyage terminé avec succès")
        return True
        
    except Exception as e:
        print("[ERREUR CLEANUP] {}".format(e))
        return False


def vider_word_recognized(memory):
    """
    Vide la clé WordRecognized dans ALMemory pour éviter les répétitions
    """
    try:
        memory.insertData("WordRecognized", [])
    except:
        pass


def initialiser_asr_vocabulaire(asr, vocabulaire):
    """
    Configure le service ASR avec un vocabulaire personnalisé
    CRITIQUE : Vide WordRecognized AVANT et APRÈS changement de vocabulaire
    """
    try:
        asr.pause(True)
        time.sleep(0.2)  # Petit délai pour s'assurer que le service est en pause
        
        asr.setVocabulary(vocabulaire, False)
        
        asr.pause(False)
        time.sleep(1.5)  # AUGMENTÉ : 1.5 secondes pour laisser le temps au service de se stabiliser
        
        return True
    except Exception as e:
        print("[ERREUR CONFIG ASR] {}".format(e))
        return False


def attendre_mot(memory, vocabulaire, timeout, tentatives_max, message_erreur, tts):
    """
    Fonction générique pour attendre la reconnaissance d'un mot du vocabulaire
    """
    tentatives = 0
    mot_detecte = None
    
    while tentatives < tentatives_max and not mot_detecte:
        print("[ECOUTE] Tentative {}/{}".format(tentatives + 1, tentatives_max))
        
        # CRITIQUE : Vider WordRecognized et attendre
        vider_word_recognized(memory)
        time.sleep(0.5)  # AUGMENTÉ : 0.5 secondes pour s'assurer que le vidage est effectif
        
        # NOUVEAU : Attendre que le robot finisse de parler + délai de silence
        # Le TTS peut prendre du temps, on attend 2 secondes de silence
        print("[ATTENTE] Délai de silence pour éviter auto-détection...")
        time.sleep(2.0)  # CRITIQUE : 2 secondes de silence AVANT d'écouter
        
        # Vider ENCORE une fois après le délai
        vider_word_recognized(memory)
        time.sleep(0.3)

        print("[ECOUTE] Début de l'écoute maintenant...")

        # Démarrer le chronomètre
        temps_debut = time.time()
        derniere_lecture = None  # Pour éviter de traiter le même mot plusieurs fois
        
        # Boucle d'écoute avec timeout
        while time.time() - temps_debut < timeout and not mot_detecte:
            try:
                result = memory.getData("WordRecognized")
                
                if result and len(result) > 0:
                    mot = result[0]
                    confiance = result[1]
                    
                    # Ignorer si c'est le même mot qu'on vient de lire
                    if mot == derniere_lecture:
                        time.sleep(0.1)
                        continue
                    
                    derniere_lecture = mot
                    
                    # Debug : afficher TOUS les mots détectés
                    print("[DEBUG] Mot capté : '{}' (confiance: {:.2f})".format(mot, confiance))
                    
                    # Vérifier que le mot fait partie du vocabulaire attendu
                    if confiance > SEUIL_CONFIANCE and mot in vocabulaire:
                        print("[DETECTION] '{}' validé !".format(mot))
                        mot_detecte = mot
                        vider_word_recognized(memory)
                        break
                    
                    # Vider pour éviter de relire le même mot en boucle
                    vider_word_recognized(memory)
            except:
                pass
            
            time.sleep(0.1)
        
        # Si aucun mot détecté, incrémenter tentatives
        if not mot_detecte:
            tentatives += 1
            
            if tentatives < tentatives_max:
                tts.say(message_erreur)
                print("[ROBOT] {}".format(message_erreur))
                # Attente après le message d'erreur aussi.
                time.sleep(2.0)
    
    return mot_detecte


# ============================================
# PHASE 1 : ATTENTE DU DÉCLENCHEUR
# ============================================

def initialiser_asr_phase1(asr):
    """
    Configure le service ASR avec le vocabulaire de la Phase 1
    """
    print("[INIT ASR PHASE 1] Configuration du vocabulaire de déclenchement...")
    
    try:
        asr.pause(True)
        time.sleep(0.2)
        
        asr.setVocabulary(PHRASES_DECLENCHEMENT, False)
        
        asr.pause(False)
        time.sleep(1.5)  # AUGMENTÉ
        
        asr.subscribe("collecte_description")
        
        print("[INIT ASR PHASE 1] Vocabulaire configuré: {}".format(PHRASES_DECLENCHEMENT))
        return True
        
    except Exception as e:
        print("[ERREUR INIT ASR PHASE 1] {}".format(e))
        return False


def phase1_attente_declencheur(asr, tts, memory):
    """
    Phase 1 : Attend qu'un mot déclencheur soit prononcé
    """
    print("\n[PHASE 1] ATTENTE DU DECLENCHEUR")
    
    # Message d'accueil
    tts.say("Bonjour. Je m'appelle Nao. Que puis-je faire pour toi aujourd'hui ?")
    print("[ROBOT] Bonjour. Je m'appelle Nao. Que puis-je faire pour toi aujourd'hui ?")
    
    # Attendre le mot déclencheur
    mot = attendre_mot(
        memory=memory,
        vocabulaire=PHRASES_DECLENCHEMENT,
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Dis trouve ou cherche.",
        tts=tts
    )
    
    if mot:
        print("[PHASE 1] SUCCES - Déclencheur '{}' détecté".format(mot))
        return True
    else:
        print("[PHASE 1] ECHEC - Aucun déclencheur détecté")
        tts.say("Je n'ai pas reçu de commande. Je vais me mettre en veille.")
        print("[ROBOT] Je n'ai pas reçu de commande. Je vais me mettre en veille.")
        return False


# ============================================
# PHASE 2 : COLLECTE DESCRIPTION DU HAUT
# ============================================

def phase2_collecte_haut(asr, tts, memory):
    """
    Phase 2 : Collecte guidée de la description du vêtement du haut
    """
    print("\n[PHASE 2] COLLECTE DESCRIPTION DU HAUT")
    
    # CRITIQUE : Vider WordRecognized AVANT de commencer la phase 2
    print("[PHASE 2] Nettoyage de WordRecognized avant de commencer...")
    vider_word_recognized(memory)
    time.sleep(1.0)  # Attendre 1 seconde pour que le vidage soit effectif
    
    # Étape 2A : Collecter la couleur
    print("[PHASE 2A] Collecte de la couleur...")
    
    if not initialiser_asr_vocabulaire(asr, COULEURS):
        print("[ERREUR] Impossible de configurer le vocabulaire des couleurs")
        return None
    
    # NOUVEAU : Vider encore une fois après changement de vocabulaire
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    tts.say("Quelle couleur pour le haut ?")
    print("[ROBOT] Quelle couleur pour le haut ?")
    
    couleur = attendre_mot(
        memory=memory,
        vocabulaire=COULEURS,
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Répète la couleur.",
        tts=tts
    )
    
    if not couleur:
        print("[PHASE 2A] ECHEC - Couleur non détectée")
        tts.say("J'ai du mal à comprendre. On arrête ici.")
        print("[ROBOT] J'ai du mal à comprendre. On arrête ici.")
        return None
    
    # Confirmation de la couleur
    tts.say("Couleur : {}".format(couleur))
    print("[CONFIRMATION] Couleur : {}".format(couleur))
    time.sleep(1.0)  # Délai plus long pour éviter que la confirmation soit captée
    
    # CRITIQUE : Vider WordRecognized avant de passer au type de vêtement
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    # Étape 2B : Collecter le type de vêtement
    print("[PHASE 2B] Collecte du type de vêtement...")
    
    if not initialiser_asr_vocabulaire(asr, VETEMENTS_HAUT):
        print("[ERREUR] Impossible de configurer le vocabulaire des vêtements")
        return None
    
    # NOUVEAU : Vider encore une fois après changement de vocabulaire
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    tts.say("Quel type de vêtement ?")
    print("[ROBOT] Quel type de vêtement ?")
    
    vetement = attendre_mot(
        memory=memory,
        vocabulaire=VETEMENTS_HAUT,
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Répète le type de vêtement.",
        tts=tts
    )
    
    if not vetement:
        print("[PHASE 2B] ECHEC - Vêtement non détecté")
        tts.say("J'ai du mal à comprendre. On arrête ici.")
        print("[ROBOT] J'ai du mal à comprendre. On arrête ici.")
        return None
    
    # Combinaison des deux informations
    description_haut = "{} {}".format(vetement, couleur)
    
    # Confirmation finale
    tts.say("D'accord, {} {}".format(vetement, couleur))
    print("[PHASE 2] SUCCES - Description du haut : '{}'".format(description_haut))
    
    time.sleep(1.0)  # Délai avant phase suivante
    
    return description_haut


# ============================================
# PHASE 3 : COLLECTE DESCRIPTION DU BAS
# ============================================

def phase3_collecte_bas(asr, tts, memory):
    """
    Phase 3 : Collecte guidée de la description du vêtement du bas
    """
    print("\n[PHASE 3] COLLECTE DESCRIPTION DU BAS")
    
    # CRITIQUE : Vider WordRecognized AVANT de commencer la phase 3
    print("[PHASE 3] Nettoyage de WordRecognized avant de commencer...")
    vider_word_recognized(memory)
    time.sleep(1.0)
    
    # Étape 3A : Collecter la couleur
    print("[PHASE 3A] Collecte de la couleur...")
    
    if not initialiser_asr_vocabulaire(asr, COULEURS):
        print("[ERREUR] Impossible de configurer le vocabulaire des couleurs")
        return None
    
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    tts.say("Maintenant la description du bas. Quelle couleur ?")
    print("[ROBOT] Maintenant la description du bas. Quelle couleur ?")
    
    couleur = attendre_mot(
        memory=memory,
        vocabulaire=COULEURS,
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Répète la couleur.",
        tts=tts
    )
    
    if not couleur:
        print("[PHASE 3A] ECHEC - Couleur non détectée")
        tts.say("J'ai du mal à comprendre. On arrête ici.")
        print("[ROBOT] J'ai du mal à comprendre. On arrête ici.")
        return None
    
    # Confirmation de la couleur
    tts.say("Couleur : {}".format(couleur))
    print("[CONFIRMATION] Couleur : {}".format(couleur))
    time.sleep(1.0)
    
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    # Étape 3B : Collecter le type de vêtement
    print("[PHASE 3B] Collecte du type de vêtement...")
    
    if not initialiser_asr_vocabulaire(asr, VETEMENTS_BAS):
        print("[ERREUR] Impossible de configurer le vocabulaire des vêtements")
        return None
    
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    tts.say("Quel type de vêtement ?")
    print("[ROBOT] Quel type de vêtement ?")
    
    vetement = attendre_mot(
        memory=memory,
        vocabulaire=VETEMENTS_BAS,
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Répète le type de vêtement.",
        tts=tts
    )
    
    if not vetement:
        print("[PHASE 3B] ECHEC - Vêtement non détecté")
        tts.say("J'ai du mal à comprendre. On arrête ici.")
        print("[ROBOT] J'ai du mal à comprendre. On arrête ici.")
        return None
    
    # Combinaison des deux informations
    description_bas = "{} {}".format(vetement, couleur)
    
    # Confirmation finale
    tts.say("D'accord, {} {}".format(vetement, couleur))
    print("[PHASE 3] SUCCES - Description du bas : '{}'".format(description_bas))
    
    time.sleep(1.0)
    
    return description_bas


# ============================================
# PHASE 4 : CONFIRMATION
# ============================================

def phase4_confirmation(asr, tts, memory, description_haut, description_bas):
    """
    Phase 4 : Demande confirmation à l'utilisateur
    """
    print("\n[PHASE 4] CONFIRMATION")
    
    # Vider avant de commencer
    vider_word_recognized(memory)
    time.sleep(1.0)
    
    if not initialiser_asr_vocabulaire(asr, ["oui", "non"]):
        print("[ERREUR] Impossible de configurer le vocabulaire de confirmation")
        return False
    
    vider_word_recognized(memory)
    time.sleep(0.5)
    
    message = "Si j'ai bien compris, la personne porte {} et {}. Correct ?".format(
        description_haut, description_bas
    )
    tts.say(message)
    print("[ROBOT] {}".format(message))
    
    reponse = attendre_mot(
        memory=memory,
        vocabulaire=["oui", "non"],
        timeout=TIMEOUT_ECOUTE,
        tentatives_max=MAX_TENTATIVES,
        message_erreur="Je n'ai pas entendu. Dis oui ou non.",
        tts=tts
    )
    
    if reponse == "oui":
        print("[PHASE 4] SUCCES - Confirmation reçue")
        return True
    elif reponse == "non":
        print("[PHASE 4] Utilisateur a refusé")
        tts.say("Sincères excuses. Peux-tu répéter s'il te plaît ?")
        print("[ROBOT] Sincères excuses. Peux-tu répéter s'il te plaît ?")
        return False
    else:
        print("[PHASE 4] Pas de réponse claire - Confirmation assumée")
        tts.say("Je vais considérer que c'est correct.")
        print("[ROBOT] Je vais considérer que c'est correct.")
        return True

# PHASE 5 : STOCKAGE ET LANCEMENT

def phase5_stockage_et_lancement(memory, tts, description_haut, description_bas):
    """
    Phase 5 : Stocke les informations dans ALMemory et lance la recherche
    """
    print("\n[PHASE 5] STOCKAGE ET LANCEMENT")
    
    try:
        config_recherche = {
            "haut": description_haut,
            "bas": description_bas,
            "recherche_active": True,
            "statut": "prete",
            "timestamp_demande": time.time()
        }
        
        memory.insertData("recherche_config", config_recherche)
        print("[STOCKAGE] Données stockées dans ALMemory : {}".format(config_recherche))
        
        memory.raiseEvent("RechercheDemarre", True)
        print("[EVENT] Événement 'RechercheDemarre' levé")
        
        tts.say("Merci pour la confirmation. Je lance la recherche de la personne.")
        print("[ROBOT] Merci pour la confirmation. Je lance la recherche de la personne.")
        
        return True
        
    except Exception as e:
        print("[ERREUR PHASE 5] {}".format(e))
        return False

# ============================================
# FONCTION PRINCIPALE APPELABLE
# ============================================

def executer_collecte_vocale(session):
    """
    Fonction principale pour exécuter toute la collecte vocale
    Peut être appelée depuis le main.py centralisé
    
    Args:
        session: Session qi connectée au robot
    
    Returns:
        int: 0 si succès, 1 si échec
    """
   
    print("MODULE VOCAL - COLLECTE DESCRIPTION")
    
    try:
        # Récupérer les services
        asr = session.service("ALSpeechRecognition")
        tts = session.service("ALTextToSpeech")
        memory = session.service("ALMemory")
        
        # Configuration langue
        asr.setLanguage("French")
        print("[VOCAL] Langue : Français")
        
        # Cleanup initial
        if not cleanup_services(asr, memory):
            print("[VOCAL] Erreur cleanup")
            tts.say("Erreur d'initialisation.")
            return 1
        
        # Boucle avec recommencement possible
        description_haut = None
        description_bas = None
        
        while True:
            # Phase 1 : Déclencheur
            if not initialiser_asr_phase1(asr):
                cleanup_services(asr, memory)
                tts.say("Erreur d'initialisation.")
                return 1
            
            if not phase1_attente_declencheur(asr, tts, memory):
                cleanup_services(asr, memory)
                return 1
            
            # Phase 2 : Haut
            description_haut = phase2_collecte_haut(asr, tts, memory)
            if not description_haut:
                cleanup_services(asr, memory)
                tts.say("Erreur lors de la collecte.")
                return 1
            
            # Phase 3 : Bas
            description_bas = phase3_collecte_bas(asr, tts, memory)
            if not description_bas:
                cleanup_services(asr, memory)
                tts.say("Erreur lors de la collecte.")
                return 1
            
            # Phase 4 : Confirmation
            if phase4_confirmation(asr, tts, memory, description_haut, description_bas):
                break  # Confirmation OK
            else:
                continue  # Recommencer
        
        # Phase 5 : Stockage
        print("\n[VOCAL] Descriptions collectées :")
        print("  - Haut : {}".format(description_haut))
        print("  - Bas  : {}".format(description_bas))
        
        if not phase5_stockage_et_lancement(memory, tts, description_haut, description_bas):
            cleanup_services(asr, memory)
            tts.say("Erreur de stockage.")
            return 1
        
        # Cleanup final
        cleanup_services(asr, memory)
        
        print("\n[VOCAL] COLLECTE TERMINEE AVEC SUCCES")
        print("[VOCAL] Données stockées dans ALMemory")
        print("[VOCAL] Événement 'RechercheDemarre' levé")
        
        return 0
        
    except Exception as e:
        print("[VOCAL] ERREUR : {}".format(e))
        import traceback
        traceback.print_exc()
        try:
            tts.say("Une erreur s'est produite.")
        except:
            pass
        return 1