#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Script de contrôle NAO v6 - Fonctions de scan et postures
# Basé sur la documentation NAOqi: http://doc.aldebaran.com/2-8/naoqi/core/
# Basé sur l'exemple main.py du projet

import qi
import argparse
import sys
import time
import math

def get_balance_data(session):
    """Récupère les données d'équilibre du gyroscope selon la doc NAOqi"""
    try:
        memory_service = session.service("ALMemory")
        
        # Utilisation des clés officielles NAOqi pour les capteurs inertiels
        # Ref: http://doc.aldebaran.com/2-8/naoqi/sensors/alinertial.html
        
        # Données du gyroscope (rad/s)
        gyro_x = memory_service.getData("Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value")
        gyro_y = memory_service.getData("Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value")
        gyro_z = memory_service.getData("Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value")
        
        # Données de l'accéléromètre (m/s²)
        accel_x = memory_service.getData("Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value")
        accel_y = memory_service.getData("Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value")
        accel_z = memory_service.getData("Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value")
        
        # Angles calculés par NAOqi (plus précis)
        try:
            angle_x = memory_service.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
            angle_y = memory_service.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value")
            use_nao_angles = True
        except:
            # Calcul manuel si les angles NAOqi ne sont pas disponibles
            angle_x = math.atan2(accel_y, accel_z) * 180.0 / math.pi  # Roll
            angle_y = math.atan2(-accel_x, math.sqrt(accel_y*accel_y + accel_z*accel_z)) * 180.0 / math.pi  # Pitch
            use_nao_angles = False
        
        # Informations batterie (bonus)
        try:
            battery = memory_service.getData("Device/SubDeviceList/Battery/Charge/Sensor/Value")
            battery_info = f" | Batterie: {battery:.1f}%"
        except:
            battery_info = ""
        
        angle_source = "NAOqi" if use_nao_angles else "Calculé"
        print(f"⚖️ EQUILIBRE ({angle_source}) - Roll: {angle_x:.2f}° | Pitch: {angle_y:.2f}°")
        print(f"   🔄 Gyroscope: X={gyro_x:.4f}, Y={gyro_y:.4f}, Z={gyro_z:.4f} rad/s")
        print(f"   📈 Accéléromètre: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f} m/s²{battery_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lecture capteurs: {e}")
        return False

def set_arms_forward(session):
    """Met les bras vers l'avant pour l'équilibre"""
    try:
        motion_service = session.service("ALMotion")
        
        print("🤲 Positionnement des bras vers l'avant pour l'équilibre...")
        
        # Position des bras pour l'équilibre
        arms_position = {
            "LShoulderPitch": 1.5,
            "LShoulderRoll": 0.3,
            "LElbowYaw": -1.2,
            "LElbowRoll": -0.5,
            "RShoulderPitch": 1.5,
            "RShoulderRoll": -0.3,
            "RElbowYaw": 1.2,
            "RElbowRoll": 0.5
        }
        
        joint_names = list(arms_position.keys())
        joint_angles = list(arms_position.values())
        
        motion_service.setAngles(joint_names, joint_angles, 0.3)
        time.sleep(2)
        
        get_balance_data(session)
        print("✅ Bras positionnés pour l'équilibre")
        
    except Exception as e:
        print(f"❌ Erreur positionnement bras: {e}")

def stand_up(session):
    """Fait lever le robot selon la doc NAOqi ALRobotPosture"""
    try:
        motion_service = session.service("ALMotion")
        posture_service = session.service("ALRobotPosture")
        tts_service = session.service("ALTextToSpeech")
        
        print("🧍 Le robot se lève...")
        
        # Vérifier la posture actuelle
        current_posture = posture_service.getPosture()
        print(f"   Posture actuelle: {current_posture}")
        
        if current_posture in ["Stand", "StandInit"]:
            print("ℹ️ Robot déjà debout")
            return
        
        # Réveiller le robot (nécessaire selon la doc)
        motion_service.wakeUp()
        time.sleep(1)
        
        # Aller en position debout - vitesse 0.8 (80%)
        # Ref: http://doc.aldebaran.com/2-8/naoqi/motion/alrobotposture.html
        success = posture_service.goToPosture("Stand", 0.8)
        
        if success:
            print("✅ Robot debout avec succès")
            tts_service.say("Je suis maintenant debout")
        else:
            print("⚠️ Échec changement de posture")
        
    except Exception as e:
        print(f"❌ Erreur pour se lever: {e}")

def sit_down(session):
    """Fait asseoir le robot selon la doc NAOqi"""
    try:
        posture_service = session.service("ALRobotPosture")
        tts_service = session.service("ALTextToSpeech")
        
        print("🪑 Le robot s'assoit...")
        
        # Vérifier la posture actuelle
        current_posture = posture_service.getPosture()
        print(f"   Posture actuelle: {current_posture}")
        
        if current_posture in ["Sit", "SitRelax"]:
            print("ℹ️ Robot déjà assis")
            return
        
        # Aller en position assise - vitesse 0.8
        success = posture_service.goToPosture("Sit", 0.8)
        
        if success:
            print("✅ Robot assis avec succès")
            tts_service.say("Je suis maintenant assis")
        else:
            print("⚠️ Échec changement de posture")
        
    except Exception as e:
        print(f"❌ Erreur pour s'asseoir: {e}")

def scan_person_vertical(session, pause_duration=2.0):
    """Scan vertical de la personne en 3 crans: pieds -> torse -> tête"""
    try:
        motion_service = session.service("ALMotion")
        
        print("🔍 === DÉBUT DU SCAN VERTICAL DE LA PERSONNE ===")
        
        # Préparer le robot avec les bras en avant
        set_arms_forward(session)
        
        # Positions pour le scan vertical (3 crans)
        scan_positions = {
            "pieds": -0.5,      # Regard vers le bas (pieds)
            "torse": -0.1,      # Regard vers le torse
            "tete": 0.3         # Regard vers le haut (tête)
        }
        
        # Parcourir les 3 positions
        for i, (position_name, pitch_angle) in enumerate(scan_positions.items(), 1):
            print(f"📍 Cran {i}/3 : Scan de la zone '{position_name.upper()}'")
            
            # Mouvement de la tête
            motion_service.setAngles("HeadPitch", pitch_angle, 0.2)
            time.sleep(1.5)
            
            # Log de l'équilibre pendant le scan
            get_balance_data(session)
            
            print(f"   📐 Position {position_name}: {pitch_angle:.2f} rad ({pitch_angle*180/math.pi:.1f}°)")
            
            # Pause pour observation/capture
            print(f"   ⏱️ Capture en cours... ({pause_duration}s)")
            time.sleep(pause_duration)
        
        print("✅ === FIN DU SCAN VERTICAL ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du scan vertical: {e}")

def scan_head_horizontal(session, steps=5):
    """Scan horizontal: tourne la tête selon les limites NAOqi"""
    try:
        motion_service = session.service("ALMotion")
        
        print("🔄 === DÉBUT DU SCAN HORIZONTAL ===")
        
        # Limites officielles NAOqi pour HeadYaw
        # Ref: http://doc.aldebaran.com/2-8/family/robots/joints_robot.html
        yaw_min, yaw_max = -2.0857, 2.0857  # Limites réelles NAO (-119.5° à +119.5°)
        yaw_step = (yaw_max - yaw_min) / (steps - 1)
        
        print(f"   Amplitude: {yaw_min*180/math.pi:.1f}° à {yaw_max*180/math.pi:.1f}° en {steps} étapes")
        
        for i in range(steps):
            yaw_angle = yaw_min + (i * yaw_step)
            
            # Position descriptive
            if i == 0:
                position = "GAUCHE MAX"
            elif i == steps - 1:
                position = "DROITE MAX"
            elif i == steps // 2:
                position = "CENTRE"
            else:
                position = f"Position {i+1}"
            
            print(f"↔️ Scan horizontal: {position}")
            
            # Mouvement de la tête
            motion_service.setAngles("HeadYaw", yaw_angle, 0.2)
            time.sleep(1.0)
            
            # Log équilibre
            get_balance_data(session)
            
            time.sleep(0.5)
        
        print("✅ === FIN DU SCAN HORIZONTAL ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du scan horizontal: {e}")

def scan_head_vertical(session, steps=5):
    """Scan vertical de la tête selon les limites NAOqi"""
    try:
        motion_service = session.service("ALMotion")
        
        print("⬆️ === DÉBUT DU SCAN VERTICAL DE LA TÊTE ===")
        
        # Limites officielles NAOqi pour HeadPitch
        # Ref: http://doc.aldebaran.com/2-8/family/robots/joints_robot.html
        pitch_min, pitch_max = -0.6720, 0.5149  # Limites réelles NAO (-38.5° à +29.5°)
        pitch_step = (pitch_max - pitch_min) / (steps - 1)
        
        print(f"   Amplitude: {pitch_min*180/math.pi:.1f}° à {pitch_max*180/math.pi:.1f}° en {steps} étapes")
        
        for i in range(steps):
            pitch_angle = pitch_min + (i * pitch_step)
            
            # Position descriptive
            if i == 0:
                position = "BAS MAX"
            elif i == steps - 1:
                position = "HAUT MAX"
            elif i == steps // 2:
                position = "MILIEU"
            else:
                position = f"Position {i+1}"
            
            print(f"⬆️ Scan vertical tête: {position}")
            
            # Mouvement de la tête
            motion_service.setAngles("HeadPitch", pitch_angle, 0.2)
            time.sleep(1.0)
            
            # Log équilibre
            get_balance_data(session)
            
            time.sleep(0.5)
        
        print("✅ === FIN DU SCAN VERTICAL DE LA TÊTE ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du scan vertical de la tête: {e}")

def reset_head_to_horizon(session):
    """Remet la tête en position horizon (regard droit devant)"""
    try:
        motion_service = session.service("ALMotion")
        
        print("🎯 === RESET DU REGARD À L'HORIZON ===")
        
        # Remettre la tête en position neutre
        head_angles = [0.0, 0.0]  # [HeadYaw, HeadPitch]
        motion_service.setAngles(["HeadYaw", "HeadPitch"], head_angles, 0.3)
        time.sleep(2.0)
        
        # Log de l'équilibre final
        get_balance_data(session)
        
        print("✅ Regard remis à l'horizon")
        
    except Exception as e:
        print(f"❌ Erreur lors du reset: {e}")

def show_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("🤖 MENU PRINCIPAL - NAO v6 CONTRÔLE")
    print("="*60)
    print("2. 🔍 Scan vertical personne (3 crans)")
    print("3. 🔄 Scan horizontal tête (gauche ↔ droite)")
    print("4. ⬆️ Scan vertical tête (bas ↔ haut)")
    print("5. 🎯 Reset regard à l'horizon")
    print("7. ⚖️ Test équilibre")
    print("8. 🧍 Se lever")
    print("9. 🪑 S'asseoir")
    print("0. ❌ Quitter")
    print("="*60)

def main(session):
    """Fonction principale avec menu interactif"""
    
    print("\n" + "="*60)
    print("🤖 CONNEXION ÉTABLIE AVEC NAO v6")
    print("="*60)
    
    # Récupération des infos robot
    try:
        memory_service = session.service("ALMemory")
        robot_name = memory_service.getData("Device/DeviceList/ChestBoard/BodyNickName/Value")
        robot_version = memory_service.getData("RobotConfig/Body/Type")
        print(f"📛 Nom du robot: {robot_name}")
        print(f"📊 Version: {robot_version}")
    except:
        print("📛 Robot: NAO v6 (infos non accessibles)")
    
    # Initialisation du robot selon la doc NAOqi
    try:
        motion_service = session.service("ALMotion")
        posture_service = session.service("ALRobotPosture")
        tts_service = session.service("ALTextToSpeech")
        
        print("🤖 Initialisation du robot...")
        
        # Vérifier l'état de stiffness (rigidité) selon la doc
        stiffness = motion_service.getStiffnesses("Body")
        print(f"   Rigidité actuelle: {max(stiffness):.2f}")
        
        motion_service.wakeUp()  # Active la rigidité à 1.0
        time.sleep(1)
        
        # Position initiale officielle
        current_posture = posture_service.getPosture()
        print(f"   Posture détectée: {current_posture}")
        
        if current_posture != "StandInit":
            print("   Passage en StandInit...")
            posture_service.goToPosture("StandInit", 0.8)
            time.sleep(2)
        
        print("✅ Robot prêt!")
        tts_service.say("Bonjour, système de contrôle prêt")
        
    except Exception as e:
        print(f"⚠️ Erreur initialisation: {e}")
    
    # Menu principal
    while True:
        show_menu()
        
        try:
            choice = input("\n🎯 Votre choix: ").strip()
            
            if choice == "2":
                scan_person_vertical(session)
                
            elif choice == "3":
                scan_head_horizontal(session)
                
            elif choice == "4":
                scan_head_vertical(session)
                
            elif choice == "5":
                reset_head_to_horizon(session)
                
            elif choice == "7":
                print("⚖️ Test de l'équilibre...")
                get_balance_data(session)
                
            elif choice == "8":
                stand_up(session)
                
            elif choice == "9":
                sit_down(session)
                
            elif choice == "0":
                print("👋 Au revoir!")
                try:
                    tts_service = session.service("ALTextToSpeech")
                    tts_service.say("Au revoir")
                    
                    # Position de repos
                    posture_service = session.service("ALRobotPosture")
                    motion_service = session.service("ALMotion")
                    posture_service.goToPosture("Crouch", 0.8)
                    time.sleep(2)
                    motion_service.rest()
                except:
                    pass
                break
                
            else:
                print("❌ Choix invalide (options: 2, 3, 4, 5, 7, 8, 9, 0)")
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé (Ctrl+C)")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.164",
                        help="Robot IP address. Default: 172.16.1.164")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE SYSTÈME NAO v6")
    print("="*60)
    print(f"📍 Tentative de connexion à {args.ip}:{args.port}...")
    
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        print("✅ Connexion réussie!")
        main(session)
    except RuntimeError:
        print("❌ Impossible de se connecter à " + args.ip + ":" + str(args.port))
        print("💡 Vérifiez que:")
        print("   - Le robot NAO est allumé")
        print("   - Vous êtes sur le même réseau")
        print("   - L'adresse IP est correcte")
        print("   - Utilisez: python nao_control.py --ip [VOTRE_IP]")
        sys.exit(1)