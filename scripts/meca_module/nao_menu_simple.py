#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Script de contrôle NAO simplifié avec menu
Utilise config.json pour l'IP du robot
"""

import sys
import time
import json
import os
import numpy as np

# Import conditionnel de qi
try:
    import qi
    QI_AVAILABLE = True
except ImportError:
    QI_AVAILABLE = False
    print("⚠ Module 'qi' non disponible. Mode démo activé.")

# Mode démo pour tester sans robot
DEMO_MODE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠ OpenCV non disponible. Fonction caméra désactivée.")

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
    
    if not QI_AVAILABLE:
        print(f"\n=== MODE DÉMO (qi non disponible) ===")
        print(f"Le module 'qi' n'est pas installé. Fonctionnalités limitées.")
        return None
    
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
        print("\nVous pouvez utiliser l'option 3 (Webcam) sans connexion au robot.")
        return None


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


def show_webcam_stream():
    """Affiche le flux de la webcam locale"""
    print("\n=== Webcam Locale (Caméra Virtuelle) ===")
    
    try:
        # Ouvrir la webcam (0 = caméra par défaut)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Impossible d'ouvrir la webcam")
            print("  Vérifiez qu'une webcam est connectée")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        # Configuration
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("✓ Webcam activée")
        print("  Résolution: 640x480")
        print("\n  Appuyez sur 'q' dans la fenêtre vidéo pour quitter")
        print("  Appuyez sur 's' pour prendre une capture")
        
        cv2.namedWindow("Webcam - Camera Virtuelle", cv2.WINDOW_NORMAL)
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("✗ Erreur lecture webcam")
                break
            
            frame_count += 1
            
            # Ajouter des informations sur l'image
            cv2.putText(frame, f"Frame: {frame_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, "Webcam Locale - Appuyez sur 'q' pour quitter", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 0), 1)
            
            # Afficher l'image
            cv2.imshow("Webcam - Camera Virtuelle", frame)
            
            # Gestion des touches
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n  Arrêt de la webcam...")
                break
            elif key == ord('s'):
                filename = f"webcam_capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"  📸 Capture sauvegardée: {filename}")
        
        # Libération des ressources
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Webcam arrêtée")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        try:
            cap.release()
            cv2.destroyAllWindows()
        except:
            pass
        input("\nAppuyez sur Entrée pour continuer...")


def show_camera_stream(session):
    """3. Flux caméra direct - Affiche le flux de la caméra frontale du robot NAO"""
    print("\n=== Flux Caméra Robot NAO ===")
    
    if not CV2_AVAILABLE:
        print("✗ OpenCV n'est pas installé. Installez-le avec: pip install opencv-python")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    # Si pas de connexion au robot
    if session is None:
        print("\n✗ Erreur: Pas de connexion au robot")
        print("  Cette fonction nécessite une connexion active au robot NAO")
        print("\n  Pour tester avec une webcam locale, utilisez: test_webcam_rapide.py")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    if DEMO_MODE:
        print("DÉMO: Affichage du flux caméra simulé...")
        print("DÉMO: Appuyez sur 'q' pour quitter")
        time.sleep(3)
        return
    
    print("\nConnexion à la caméra frontale du robot...")
    
    try:
        video_service = session.service("ALVideoDevice")
        
        # Configuration de la caméra
        # Caméra 0 = Top (frontale), 1 = Bottom
        camera_id = 0  # Caméra frontale
        resolution = 2  # VGA (640x480)
        color_space = 11  # RGB
        fps = 15  # 15 FPS (plus stable que 30)
        
        # S'abonner au flux vidéo
        print("  Abonnement au flux vidéo...")
        subscriber_id = video_service.subscribeCamera(
            "python_nao_camera", camera_id, resolution, color_space, fps
        )
        
        print("✓ Flux caméra activé !")
        print("  Résolution: 640x480 (VGA)")
        print("  Caméra: Frontale (Top Camera)")
        print("  FPS: 15")
        print("\n  👁️  Fenêtre vidéo en cours d'ouverture...")
        print("  Appuyez sur 'q' dans la fenêtre pour quitter")
        
        cv2.namedWindow("NAO Robot - Camera Frontale", cv2.WINDOW_NORMAL)
        
        while True:
            # Récupérer l'image
            nao_image = video_service.getImageRemote(subscriber_id)
            
            if nao_image is None:
                print("✗ Impossible de récupérer l'image")
                break
            
            # Extraire les données de l'image
            width = nao_image[0]
            height = nao_image[1]
            image_data = nao_image[6]
            
            # Convertir en array numpy
            image = np.frombuffer(image_data, dtype=np.uint8)
            image = image.reshape((height, width, 3))
            
            # Convertir RGB vers BGR pour OpenCV
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Afficher l'image
            cv2.imshow("NAO Robot - Camera Frontale", image_bgr)
            
            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n  Arrêt du flux caméra...")
                break
        
        # Se désabonner
        video_service.unsubscribe(subscriber_id)
        cv2.destroyAllWindows()
        print("✓ Flux caméra arrêté")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        try:
            video_service.unsubscribe(subscriber_id)
            cv2.destroyAllWindows()
        except:
            pass
        input("\nAppuyez sur Entrée pour continuer...")


def scan_vertical_4_crans(session):
    """4. Scan vertical 4 crans - Scan du BAS vers le HAUT avec 4 secondes entre chaque"""
    print("\n=== Scan Vertical 4 Crans (Bas → Haut) ===")
    
    if DEMO_MODE:
        positions = ["Genoux", "Torse", "Poitrine", "Tête"]
        for i, pos in enumerate(positions, 1):
            print(f"DÉMO: Cran {i}/4 - {pos}")
            time.sleep(4)
        return
    
    try:
        motion = session.service("ALMotion")
        
        # Activer le contrôle de la tête
        motion.setStiffnesses("Head", 1.0)
        
        # 4 positions de scan vertical - DU BAS VERS LE HAUT
        # Pitch: négatif = vers le haut, positif = vers le bas
        positions = [
            ("Genoux", 0.25),      # Bas (commence ici)
            ("Torse", -0.05),      # Centre
            ("Poitrine", -0.25),   # Haut
            ("Tête", -0.45)        # Très haut
        ]
        
        print("Début du scan vertical en 4 crans (du bas vers le haut)...")
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
    """5. Scan vertical avec bras - Les bras vers l'avant permettent de regarder plus haut"""
    print("\n=== Scan Vertical avec Bras Avant (Haut → Bas) ===")
    
    if DEMO_MODE:
        positions = ["Tête (bras avant)", "Poitrine", "Torse", "Genoux"]
        for i, pos in enumerate(positions, 1):
            print(f"DÉMO: Cran {i}/4 - {pos}")
            time.sleep(4)
        print("DÉMO: Bras reviennent en position normale")
        return
    
    if session is None:
        print("✗ Erreur: Pas de connexion au robot")
        print("  Cette fonction nécessite une connexion active au robot NAO")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    try:
        motion = session.service("ALMotion")
        
        print("\n  ⚙️  PHASE 1: Préparation - Bras vers l'avant")
        
        # Activer le contrôle de la tête et des bras
        motion.setStiffnesses(["Head", "LArm", "RArm"], 1.0)
        time.sleep(0.5)
        
        print("  → Positionnement des bras vers l'avant...")
        
        # Bras vers l'avant (angles plus sûrs)
        names = ["LShoulderPitch", "LShoulderRoll", "RShoulderPitch", "RShoulderRoll"]
        angles = [0.8, 0.15, 0.8, -0.15]  # Bras vers l'avant, légèrement écartés
        speed = 0.15
        
        motion.setAngles(names, angles, speed)
        time.sleep(2)
        
        print("\n  📹 PHASE 2: Scan vertical du HAUT vers le BAS")
        
        # 4 positions de scan vertical - DU HAUT VERS LE BAS
        # Pitch: négatif = vers le haut, positif = vers le bas
        positions = [
            ("Très haut", -0.50),    # Très haut (commence ici)
            ("Tête", -0.30),         # Haut
            ("Poitrine", -0.10),     # Centre-haut
            ("Torse", 0.15)          # Bas
        ]
        
        for i, (nom, pitch) in enumerate(positions, 1):
            print(f"  Cran {i}/4 - {nom} (pitch: {pitch:.2f})")
            motion.setAngles("HeadPitch", pitch, 0.15)
            time.sleep(4)  # 4 secondes entre chaque cran
        
        print("\n  🔄 PHASE 3: Retour à la position normale")
        
        # Remettre la tête au centre
        print("  → Tête au centre...")
        motion.setAngles("HeadPitch", 0.0, 0.15)
        time.sleep(1.5)
        
        # Bras le long du corps
        print("  → Bras le long du corps...")
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.15)
        motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.1, -0.1], 0.15)
        time.sleep(2)
        
        print("\n✓ Scan vertical avec bras terminé")
        print("  Les bras en avant ont permis de regarder plus haut !")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        print("  Détails:", str(e))
        import traceback
        traceback.print_exc()


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
    print("3. 📹 Flux caméra frontale du robot NAO")
    print("4. Scan vertical 4 crans (Bas → Haut, 4s/cran)")
    print("5. 🔥 Scan avec bras avant (regarde plus haut !)")
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
                show_camera_stream(session)
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
