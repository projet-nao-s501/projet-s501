#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Script de contrôle NAO simplifié avec menu
Utilise config.json pour l'IP du robot
"""

import qi
import sys
import time
import json
import os

# Mode démo pour tester sans robot
DEMO_MODE = False

def load_config():
    """Charge la configuration depuis config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config['robot_ip'], config['robot_port']
    except Exception as e:
        print(f"Erreur lors du chargement de config.json: {e}")
        print("Utilisation des valeurs par défaut...")
        return "172.16.1.164", 9559


def connect_to_nao():
    """Connexion au robot NAO"""
    robot_ip, robot_port = load_config()
    
    if DEMO_MODE:
        print(f"\n=== MODE DÉMO ACTIVÉ ===")
        print(f"Simulation de connexion à {robot_ip}:{robot_port}")
        return None
    
    print(f"\nConnexion au robot NAO sur {robot_ip}:{robot_port}...")
    session = qi.Session()
    try:
        session.connect(f"tcp://{robot_ip}:{robot_port}")
        print("✓ Connexion réussie!")
        return session
    except RuntimeError as e:
        print(f"✗ Impossible de se connecter au robot NAO")
        print(f"Erreur: {e}")
        sys.exit(1)


def stand_up(session):
    """1. Debout - Met le robot en position debout"""
    print("\n=== Position Debout ===")
    
    if DEMO_MODE:
        print("DÉMO: Robot se met debout...")
        time.sleep(2)
        return
    
    try:
        motion = session.service("ALMotion")
        posture = session.service("ALRobotPosture")
        
        # Réveiller le robot
        motion.wakeUp()
        time.sleep(1)
        
        # Position debout
        posture.goToPosture("StandInit", 0.5)
        print("✓ Robot en position debout")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def sit_down(session):
    """2. S'asseoir - Met le robot en position assise"""
    print("\n=== Position Assise ===")
    
    if DEMO_MODE:
        print("DÉMO: Robot s'assoit...")
        time.sleep(2)
        return
    
    try:
        posture = session.service("ALRobotPosture")
        
        # Position assise
        posture.goToPosture("Sit", 0.5)
        print("✓ Robot assis")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def start_virtual_camera(session):
    """3. Caméra virtuelle - Lance le flux de caméra virtuelle"""
    print("\n=== Caméra Virtuelle ===")
    print("Pour lancer la caméra virtuelle, utilisez:")
    print("  python virtual_cam_simple.py")
    print("\nOu appuyez sur F5 dans VS Code avec la config 'NAO Camera Simple'")
    input("\nAppuyez sur Entrée pour continuer...")


def scan_vertical_4_crans(session):
    """4. Scan vertical 4 crans - Scan de bas en haut avec 4 secondes entre chaque"""
    print("\n=== Scan Vertical 4 Crans ===")
    
    if DEMO_MODE:
        positions = ["Pieds", "Genoux", "Torse", "Tête"]
        for i, pos in enumerate(positions, 1):
            print(f"DÉMO: Cran {i}/4 - {pos}")
            time.sleep(4)
        return
    
    try:
        motion = session.service("ALMotion")
        
        # Activer le contrôle de la tête
        motion.setStiffnesses("Head", 1.0)
        
        # 4 positions de scan vertical
        # Pitch: négatif = vers le bas, positif = vers le haut
        positions = [
            ("Pieds", 0.45),      # Très bas
            ("Genoux", 0.15),     # Bas
            ("Torse", -0.15),     # Centre/légèrement haut
            ("Tête", -0.38)       # Haut
        ]
        
        print("Début du scan vertical en 4 crans...")
        for i, (nom, pitch) in enumerate(positions, 1):
            print(f"  Cran {i}/4 - {nom} (pitch: {pitch:.2f})")
            motion.setAngles("HeadPitch", pitch, 0.15)
            time.sleep(4)  # 4 secondes entre chaque cran
        
        # Retour au centre
        motion.setAngles("HeadPitch", 0.0, 0.15)
        print("✓ Scan vertical terminé")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def scan_vertical_avec_bras(session):
    """5. Scan vertical avec bras - Les bras montent vers l'avant pour équilibrer"""
    print("\n=== Scan Vertical avec Compensation Bras ===")
    
    if DEMO_MODE:
        positions = ["Pieds", "Genoux", "Torse", "Tête (bras en avant)"]
        for i, pos in enumerate(positions, 1):
            print(f"DÉMO: Cran {i}/4 - {pos}")
            time.sleep(4)
        print("DÉMO: Bras reviennent en position normale")
        return
    
    try:
        motion = session.service("ALMotion")
        
        # Activer le contrôle de la tête et des bras
        motion.setStiffnesses(["Head", "LArm", "RArm"], 1.0)
        
        # Positions des bras vers l'avant pour compensation
        # ShoulderPitch: angle d'épaule (+ = vers l'avant/bas, - = vers l'arrière/haut)
        # ShoulderRoll: écartement latéral
        arm_forward = {
            "LShoulderPitch": 1.0,   # Bras gauche vers l'avant
            "LShoulderRoll": 0.15,   # Légèrement écarté
            "RShoulderPitch": 1.0,   # Bras droit vers l'avant
            "RShoulderRoll": -0.15   # Légèrement écarté
        }
        
        # 4 positions de scan vertical
        positions = [
            ("Pieds", 0.45),
            ("Genoux", 0.15),
            ("Torse", -0.15),
            ("Tête", -0.38)
        ]
        
        print("Début du scan vertical avec compensation des bras...")
        
        # Mettre les bras vers l'avant pour la position haute
        print("  → Bras vers l'avant pour compensation...")
        for joint, angle in arm_forward.items():
            motion.setAngles(joint, angle, 0.15)
        time.sleep(2)
        
        # Scan avec les positions
        for i, (nom, pitch) in enumerate(positions, 1):
            print(f"  Cran {i}/4 - {nom} (pitch: {pitch:.2f})")
            motion.setAngles("HeadPitch", pitch, 0.15)
            time.sleep(4)  # 4 secondes entre chaque cran
        
        # Remettre les bras le long du corps
        print("  → Bras en position normale...")
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.15)
        motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.1, -0.1], 0.15)
        
        # Retour au centre de la tête
        motion.setAngles("HeadPitch", 0.0, 0.15)
        time.sleep(1)
        
        print("✓ Scan vertical avec bras terminé")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def scan_tete_complet(session):
    """6. Scan tête complet - Gauche/Droite puis Bas/Haut et retour au centre"""
    print("\n=== Scan Tête Complet ===")
    
    if DEMO_MODE:
        mouvements = [
            "Tête → Gauche maximum",
            "Tête → Droite maximum", 
            "Tête → Centre",
            "Tête → Bas maximum",
            "Tête → Haut maximum",
            "Tête → Centre"
        ]
        for mouv in mouvements:
            print(f"DÉMO: {mouv}")
            time.sleep(2)
        return
    
    try:
        motion = session.service("ALMotion")
        
        # Activer le contrôle de la tête
        motion.setStiffnesses("Head", 1.0)
        
        print("Scan horizontal de la tête...")
        # Yaw: rotation gauche/droite (+ = gauche, - = droite)
        print("  → Gauche maximum")
        motion.setAngles("HeadYaw", 2.0, 0.15)  # Gauche max (~119°)
        time.sleep(2)
        
        print("  → Droite maximum")
        motion.setAngles("HeadYaw", -2.0, 0.15)  # Droite max (~119°)
        time.sleep(2)
        
        print("  → Centre")
        motion.setAngles("HeadYaw", 0.0, 0.15)  # Centre
        time.sleep(2)
        
        print("Scan vertical de la tête...")
        # Pitch: inclinaison haut/bas (+ = bas, - = haut)
        print("  → Bas maximum")
        motion.setAngles("HeadPitch", 0.51, 0.15)  # Bas max (~29°)
        time.sleep(2)
        
        print("  → Haut maximum")
        motion.setAngles("HeadPitch", -0.67, 0.15)  # Haut max (~38°)
        time.sleep(2)
        
        print("  → Centre")
        motion.setAngles("HeadPitch", 0.0, 0.15)  # Centre
        time.sleep(1)
        
        print("✓ Scan tête complet terminé")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def point_and_alert(session):
    """7. Pointer et alerter - Pointe un doigt vers le haut et dit 'Intrus trouvé'"""
    print("\n=== Alerte Intrus ===")
    
    if DEMO_MODE:
        print("DÉMO: Lève le bras droit et pointe vers le haut...")
        time.sleep(2)
        print('DÉMO: Dit "Intrus trouvé!"')
        time.sleep(2)
        print("DÉMO: Remet le bras en position normale")
        return
    
    try:
        motion = session.service("ALMotion")
        tts = session.service("ALTextToSpeech")
        
        # Activer le contrôle du bras droit
        motion.setStiffnesses("RArm", 1.0)
        
        print("  → Lève le bras et pointe vers le haut...")
        
        # Position pour pointer vers le haut avec le bras droit
        # ShoulderPitch: vers l'avant/haut
        # ShoulderRoll: écartement
        # ElbowYaw: rotation du coude
        # ElbowRoll: flexion du coude
        # WristYaw: rotation du poignet
        # Hand: ouverture de la main
        
        pointing_position = {
            "RShoulderPitch": -1.3,   # Bras vers le haut
            "RShoulderRoll": -0.3,    # Légèrement écarté du corps
            "RElbowYaw": 1.2,         # Rotation du coude
            "RElbowRoll": 0.5,        # Coude légèrement plié
            "RWristYaw": 0.0,         # Poignet droit
            "RHand": 0.0              # Main fermée (doigt pointé)
        }
        
        for joint, angle in pointing_position.items():
            motion.setAngles(joint, angle, 0.2)
        
        time.sleep(2)
        
        # Dire le message
        print("  → 'Intrus trouvé!'")
        tts.say("Intrus trouvé!")
        time.sleep(1)
        
        # Remettre le bras en position normale
        print("  → Bras en position normale...")
        motion.setAngles("RShoulderPitch", 1.5, 0.2)
        motion.setAngles("RShoulderRoll", -0.1, 0.2)
        motion.setAngles("RElbowRoll", 0.5, 0.2)
        motion.setAngles("RElbowYaw", 1.2, 0.2)
        motion.setAngles("RHand", 0.6, 0.2)
        time.sleep(1)
        
        print("✓ Alerte terminée")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def reset_position(session):
    """8. Reset position - Remet le robot en position neutre (tête et mains)"""
    print("\n=== Reset Position ===")
    
    if DEMO_MODE:
        print("DÉMO: Tête revient au centre...")
        print("DÉMO: Bras reviennent en position normale...")
        print("DÉMO: Mains s'ouvrent...")
        time.sleep(2)
        return
    
    try:
        motion = session.service("ALMotion")
        
        # Activer le contrôle
        motion.setStiffnesses(["Head", "LArm", "RArm"], 1.0)
        
        print("  → Reset de la tête...")
        # Tête au centre
        motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], 0.2)
        
        print("  → Reset des bras...")
        # Bras en position neutre
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.2)
        motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.1, -0.1], 0.2)
        motion.setAngles(["LElbowYaw", "RElbowYaw"], [-1.2, 1.2], 0.2)
        motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.2)
        
        print("  → Reset des mains...")
        # Mains ouvertes
        motion.setAngles(["LHand", "RHand"], [0.6, 0.6], 0.2)
        
        time.sleep(2)
        print("✓ Position reset terminée")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")


def display_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print("     MENU DE CONTRÔLE NAO - PROJET S501")
    print("="*50)
    print("1. Debout")
    print("2. S'asseoir")
    print("3. Caméra virtuelle")
    print("4. Scan vertical 4 crans (4s entre chaque)")
    print("5. Scan vertical avec bras avant (compensation)")
    print("6. Scan tête complet (gauche/droite + bas/haut)")
    print("7. Pointer vers le haut + 'Intrus trouvé'")
    print("8. Reset position (tête et mains)")
    print("9. Quitter")
    print("="*50)


def main():
    """Fonction principale avec menu"""
    global DEMO_MODE
    
    print("\n" + "="*50)
    print("   SYSTÈME DE CONTRÔLE NAO - PROJET S501")
    print("="*50)
    
    # Demander le mode
    mode = input("\nMode DÉMO (sans robot) ? (o/n) [n]: ").strip().lower()
    DEMO_MODE = (mode == 'o' or mode == 'oui')
    
    # Connexion au robot
    session = connect_to_nao()
    
    # Boucle principale
    while True:
        display_menu()
        
        try:
            choice = input("\nVotre choix (1-9): ").strip()
            
            if choice == '1':
                stand_up(session)
            elif choice == '2':
                sit_down(session)
            elif choice == '3':
                start_virtual_camera(session)
            elif choice == '4':
                scan_vertical_4_crans(session)
            elif choice == '5':
                scan_vertical_avec_bras(session)
            elif choice == '6':
                scan_tete_complet(session)
            elif choice == '7':
                point_and_alert(session)
            elif choice == '8':
                reset_position(session)
            elif choice == '9':
                print("\nAu revoir!")
                break
            else:
                print("\n✗ Choix invalide. Veuillez choisir entre 1 et 9.")
                
        except KeyboardInterrupt:
            print("\n\nInterruption par l'utilisateur.")
            break
        except Exception as e:
            print(f"\n✗ Erreur: {e}")
    
    # Nettoyage
    if session and not DEMO_MODE:
        try:
            motion = session.service("ALMotion")
            motion.rest()
        except:
            pass
    
    print("\nProgramme terminé.")


if __name__ == "__main__":
    main()
