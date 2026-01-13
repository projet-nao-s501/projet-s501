#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import sys
import time
import json
import os
import math
import numpy as np
import cv2
import subprocess 
from ultralytics import YOLO

# Import de qi (NAOqi)
try:
    import qi
except ImportError:
    print("CRITIQUE: Module 'qi' introuvable. Avez-vous activé 'source nao_env/bin/activate' ?")
    sys.exit(1)

# --- CONFIGURATION ---
ROBOT_IP = "172.16.1.163" 
ROBOT_PORT = 9559
MODEL_PATH = "best.pt"

# Chargement IP config.json
if os.path.exists("config.json"):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            ROBOT_IP = config.get("robot_ip", ROBOT_IP)
            ROBOT_PORT = config.get("robot_port", ROBOT_PORT)
            print(f"-> Configuration chargée : IP {ROBOT_IP}")
    except: pass

# --- VARIABLES GLOBALES ---
calib_data = {"y_bias": 0.0, "rot_mult": 1.0}
slam_process = None 

# --- FONCTIONS UTILITAIRES ---

def load_calibration():
    global calib_data
    if os.path.exists("calib_save.json"):
        try:
            with open("calib_save.json", "r") as f:
                calib_data = json.load(f)
            print(f"✓ Calibration chargée : Y={calib_data['y_bias']}, Rot={calib_data['rot_mult']}")
        except:
            print("! Fichier calibration corrompu, retour aux valeurs par défaut.")

def save_calibration():
    with open("calib_save.json", "w") as f:
        json.dump(calib_data, f)
    print("✓ Calibration sauvegardée !")

def connect_to_nao():
    session = qi.Session()
    try:
        print(f"Connexion au robot {ROBOT_IP}:{ROBOT_PORT}...")
        session.connect(f"tcp://{ROBOT_IP}:{ROBOT_PORT}")
        print("✓ Connecté avec succès !")
        return session
    except RuntimeError:
        print(f"✗ IMPOSSIBLE de se connecter à {ROBOT_IP}")
        sys.exit(1)

def stand_up(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)
    print("✓ Robot Debout")
    
    

def sit_down(session):
    motion = session.service("ALMotion")
    posture = session.service("ALRobotPosture")
    posture.goToPosture("Sit", 0.5)
    motion.rest()
    print("✓ Robot Assis (Moteurs coupés)")

def calibration_interactive(session):
    motion = session.service("ALMotion")
    stand_up(session)
    while True:
        print("\n" + "-"*40)
        print(f"RÉGLAGES : Biais Y = {calib_data['y_bias']:.3f} | Mult Rot = {calib_data['rot_mult']:.3f}")
        print("1. TEST MARCHE DROITE (1m)")
        print("2. TEST ROTATION (360°)")
        print("0. Retour")
        c = input("Choix : ")
        if c == "1":
            motion.moveTo(1.0, 0.0 + calib_data['y_bias'], 0.0)
            ajust = input("Correction (ex: l0.05 ou r0.05) : ").lower().strip()
            if len(ajust) > 1:
                val = float(ajust[1:])
                if ajust[0] == 'l': calib_data['y_bias'] += val
                elif ajust[0] == 'r': calib_data['y_bias'] -= val
        elif c == "2":
            target = 2 * math.pi
            motion.moveTo(0.0, 0.0, target * calib_data['rot_mult'])
            ajust = input("Correction (ex: l0.1 ou r0.1) : ").lower().strip()
            if len(ajust) > 1:
                val = float(ajust[1:])
                if ajust[0] == 'l': calib_data['rot_mult'] += val
                elif ajust[0] == 'r': calib_data['rot_mult'] -= val
        elif c == "0":
            save_calibration()
            break

def test_ia_shoes(session):
    print("\n--- TEST IA CHAUSSURES (Statique) ---")
    if not os.path.exists(MODEL_PATH):
        print(f"Erreur: {MODEL_PATH} absent.")
        return
    model = YOLO(MODEL_PATH)
    video = session.service("ALVideoDevice")
    sub = video.subscribeCamera(f"Yolo_{int(time.time())}", 1, 1, 11, 30)
    
    try:
        while True:
            img = video.getImageRemote(sub)
            if img:
                arr = np.frombuffer(img[6], dtype=np.uint8).reshape((img[1], img[0], 3))
                frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                results = model(frame, conf=0.5, verbose=False)
                for r in results:
                    frame = r.plot()
                    for box in r.boxes:
                        print(f"👟 Chaussure/Personne détectée! Conf: {box.conf[0]:.2f}")
                
                cv2.imshow("IA Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
    except KeyboardInterrupt: pass
    finally:
        video.unsubscribe(sub)
        cv2.destroyAllWindows()

# --- FONCTIONS SLAM ---

def start_slam_background():
    print("🚀 Démarrage du moteur SLAM (ORB-SLAM3)...")
    env = os.environ.copy()
    cwd = os.getcwd()
    env["LD_LIBRARY_PATH"] = os.path.join(cwd, "libs") + ":" + env.get("LD_LIBRARY_PATH", "")
    cmd = ["./mono_euroc", "ORBvoc.txt", "EuRoC.yaml", ".", "."]
    try:
        proc = subprocess.Popen(cmd, env=env, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ SLAM actif (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"❌ Erreur lancement SLAM: {e}")
        return None

def get_slam_position():
    try:
        if os.path.exists("CameraTrajectory.txt"):
            with open("CameraTrajectory.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    last = lines[-1].strip().split()
                    if len(last) > 3:
                        return float(last[1]), float(last[3]) 
    except: pass
    return 0.0, 0.0

# --- FONCTION PRINCIPALE D'EXPLORATION ---

def autonomous_exploration(session):
    
    # --- 1. INITIALISATION DES SERVICES ---
    motion = session.service("ALMotion")
    memory = session.service("ALMemory")
    video = session.service("ALVideoDevice")
    tts = session.service("ALTextToSpeech")
    
    stand_up(session)
    
    # Position de base pour le SLAM
    motion.setStiffnesses("Head", 1.0)
    motion.setAngles("HeadPitch", -0.1, 0.1)

    # --- 2. LANCEMENT SLAM & IA ---
    global slam_process
    slam_process = start_slam_background()
    
    print("Chargement YOLO...")
    model = YOLO(MODEL_PATH)
    
    # Abonnement Caméra
    sub = video.subscribeCamera(f"Auto_{int(time.time())}", 1, 1, 11, 30)

    # --- 3. DÉFINITION DE LA FONCTION DE SCAN (INTERNE) ---
    def scan_vertical_sequence():
        """Effectue la séquence de scan (Bas->Haut) directement ici"""
        print("\n--- 🕵️ DÉBUT SÉQUENCE SCAN ---")
        
        # Petite fonction interne pour attendre 7s sans figer l'image
        def wait_7s_active(step_name):
            print(f"   -> Scan {step_name} (7s)...")
            start = time.time()
            while time.time() - start < 7.0:
                img_scan = video.getImageRemote(sub)
                if img_scan:
                    arr = np.frombuffer(img_scan[6], dtype=np.uint8).reshape((img_scan[1], img_scan[0], 3))
                    frame_scan = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                    cv2.putText(frame_scan, f"SCAN: {step_name}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow("Exploration Robot", frame_scan)
                    cv2.waitKey(1)
        
        # Vérification équilibre rapide
        try:
            ax = memory.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
            ay = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value")
            if abs(ax) > 0.35 or abs(ay) > 0.35:
                print("⚠️ Trop instable pour scanner.")
                return
        except: pass


        
        # ÉTAPE 1 : pied jambe
        motion.setAngles("HeadPitch", -0.5, 0.1) # Tête vers le haut
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-0.5, -0.5], 0.1) # Bras levés
        wait_7s_active("HAUT (Visage)")

        # ÉTAPE 2 : haut tête
        motion.setAngles("HeadPitch", -0.6, 0.1) # Plafond
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-0.4, -0.4], 0.05) # Bras levés
        motion.setAngles(["LElbowRoll", "RElbowRoll"], [0, 0], 0.05) # Bras tendu
        motion.setAngles(["LHipPitch", "RHipPitch"], [-0.3, -0.3], 0.05)
        wait_7s_active("HAUT (Visage)")
        
        # RETOUR
        print("--- FIN SCAN ---")
        motion.setAngles("HeadPitch", -0.1, 0.1)
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.1)

    # --- 4. INIT SLAM (Tête G/D) ---
    tts.say("Initialisation du slam.")
    motion.setAngles("HeadYaw", 0.4, 0.08)
    time.sleep(3.0)
    motion.setAngles("HeadYaw", -0.4, 0.08)
    time.sleep(3.0)
    motion.setAngles("HeadYaw", 0.0, 0.08)
    print("✅ C'est parti !")

    visited_zones = set()

    # --- 5. BOUCLE PRINCIPALE ---
    try:
        while True:
            # A. SONARS (Murs)
            left = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            right = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            
            if left < 0.45 or right < 0.45:
                print(f"🛑 MUR (L:{left:.2f} R:{right:.2f})")
                motion.stopMove()
                tts.say("Mur.")
                motion.moveTo(-0.15, 0, 0)
                if left < right: motion.moveTo(0, 0, -0.6)
                else: motion.moveTo(0, 0, 0.6)
                continue

            # B. VISION (Détection Humain)
            img = video.getImageRemote(sub)
            person_detected = False
            
            if img:
                arr = np.frombuffer(img[6], dtype=np.uint8).reshape((img[1], img[0], 3))
                frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                
                # YOLO
                results = model(frame, verbose=False, conf=0.5)
                for r in results:
                    for box in r.boxes:
                        # On vérifie si l'objet est assez gros (>15% image)
                        width = box.xyxy[0][2] - box.xyxy[0][0]
                        if width > (img[0] * 0.15):
                            person_detected = True
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                
                cv2.imshow("Exploration Robot", frame)
                cv2.waitKey(1)

            # C. DÉCLENCHEMENT DU SCAN
            if person_detected:
                print("🛑 HUMAIN DÉTECTÉ -> Lancement Scan Vertical")
                motion.stopMove()
                tts.say("Personne détecté.")
                
                # APPEL DE LA FONCTION INTERNE
                scan_vertical_sequence()
                
                # Évitement après le scan
                tts.say("Fin scan.")
                
                motion.moveTo(0, 0, 0.8) # Tourne
                continue

            # D. SLAM & MARCHE
            x, z = get_slam_position()
            if x != 0.0 or z != 0.0:
                cx, cz = int(round(x/0.5)), int(round(z/0.5))
                # si case jamais visitée
                if (cx, cz) not in visited_zones:
                    visited_zones.add((cx, cz))
                    print(f"📍 Zone: {(cx, cz)} (Total: {len(visited_zones)})")
                    # visité 30 cases ce qui represente environs 7.5m carré
                    if len(visited_zones) >= 30:
                        motion.stopMove()
                        tts.say("Terminé.")
                        break

            motion.move(0.08, 0, 0)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Arrêt.")
    finally:
        motion.stopMove()
        video.unsubscribe(sub)
        cv2.destroyAllWindows()
        if slam_process: slam_process.terminate()

# --- MENU PRINCIPAL ---

def main():
    load_calibration()
    session = connect_to_nao()
    
    while True:
        print("\n" + "="*45)
        print(" 🤖  NAO CONTROL V2 - AVEC SLAM & IA  🤖")
        print("="*45)
        print("1. Debout")
        print("2. Assis")
        print("3. Calibration")
        print("4. Test IA (Statique)")
        print("5. 🚀 LANCER L'EXPLORATION AUTONOME")
        print("0. Quitter")
        
        c = input("Choix : ")
        if c == '1': stand_up(session)
        elif c == '2': sit_down(session)
        elif c == '3': calibration_interactive(session)
        elif c == '4': test_ia_shoes(session)
        elif c == '5': autonomous_exploration(session)
        elif c == '0': 
            sit_down(session)
            break
        else: print("Choix inconnu.")

if __name__ == "__main__":
    main()