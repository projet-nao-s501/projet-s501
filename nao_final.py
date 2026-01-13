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
from scripts.ia_module.detection_formes import detection_formes

# Import de qi (NAOqi)
try:
    import qi
except ImportError:
    print("CRITIQUE: Module 'qi' introuvable. Avez-vous activé 'source nao_env/bin/activate' ?")
    sys.exit(1)

# --- VARIABLES GLOBALES ---
calib_data = {"y_bias": 0.0, "rot_mult": 1.0}
slam_process = None 
MODEL_PATH = "best.pt"

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

yolo_model = None 
visited_zones = set()

def initialiser_exploration(session):
    """Effectue la séquence de démarrage indispensable pour le SLAM et la posture."""
    motion = session.service("ALMotion")
    tts = session.service("ALTextToSpeech")
    
    print("--- 🏁 INITIALISATION ---")
    stand_up(session) # Ta fonction existante
    
    # Position de base et rigidité
    motion.setStiffnesses("Head", 1.0)
    motion.setAngles("HeadPitch", -0.1, 0.1)

    # Séquence de regard G/D pour le SLAM (Crucial pour la cartographie)
    tts.say("Initialisation du slam.")
    motion.setAngles("HeadYaw", 0.4, 0.08)
    time.sleep(3.0)
    motion.setAngles("HeadYaw", -0.4, 0.08)
    time.sleep(3.0)
    motion.setAngles("HeadYaw", 0.0, 0.08)
    print("✅ SLAM Initialisé. Prêt pour l'exploration.")

def detect_person(img, model):
    """Analyse l'image et vérifie si un humain est à proximité (>15% de largeur)."""
    results = model(img, verbose=False, conf=0.5)
    person_detected = False
    
    for r in results:
        for box in r.boxes:
            # .item() convertit le Tensor en nombre standard pour éviter l'erreur de comparaison
            box_width = (box.xyxy[0][2] - box.xyxy[0][0]).item()
            
            # Seuil de proximité basé sur la largeur de l'image
            if box_width > (img.shape[1] * 0.15):
                person_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
    return person_detected, img

def wait_and_update_display(video_service, name_id, step_name, duration=7.0):
    """Maintient le flux vidéo "Live" et l'affichage pendant les pauses de mouvement."""
    start = time.time()
    while time.time() - start < duration:
        img_raw = video_service.getImageRemote(name_id)
        if img_raw:
            # Reconstruction de l'image pour affichage
            width, height = img_raw[0], img_raw[1]
            arr = np.frombuffer(img_raw[6], dtype=np.uint8).reshape((height, width, 3))
            frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            
            # Overlay d'informations
            cv2.putText(frame, f"SCAN: {step_name}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Exploration Robot", frame)
            
            # Appel de ta fonction d'analyse de formes sur le buffer frais
            detection_formes(arr) 
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def perform_vertical_scan(session, video_service, name_id):
    motion = session.service("ALMotion")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")
    
    # --- 1. ARRÊT ET STABILISATION ---
    motion.stopMove()
    time.sleep(0.5) # Crucial : on attend que le robot ne balance plus
    
    # --- 2. VÉRIFICATION INERTIELLE (Sécurité chute) ---
    try:
        ax = memory.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value")
        ay = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value")
        if abs(ax) > 0.25 or abs(ay) > 0.25: # Plus strict que l'original
            print("⚠️ Robot instable, scan annulé pour éviter la chute.")
            return
    except: pass

    print("\n--- 🕵️ DÉBUT SCAN SÉCURISÉ ---")
    tts.say("Personne détectée.")
    tts.say("Peux-tu reculer de trois pas s'il-te-plait")
    time.sleep(5.0)

    # ÉTAPE 1 : Bas (Tête + Épaules) - Peu de risque ici
    motion.setAngles("HeadPitch", -0.6, 0.1)
    motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-0.5, -0.5], 0.1)
    wait_and_update_display(video_service, name_id, "BAS", 7.0)

    # ÉTAPE 2 : Haut (Hanches + Coudes) - ZONE À RISQUE
    # On réduit légèrement la vitesse (0.03 au lieu de 0.05) pour plus de douceur
    motion.setAngles("HeadPitch", -0.6720, 0.1)
    motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-0.4, -0.4], 0.03)
    motion.setAngles(["LElbowRoll", "RElbowRoll"], [0, 0], 0.03)
    motion.setAngles(["LHipPitch", "RHipPitch"], [-0.3, -0.3], 0.03) 
    wait_and_update_display(video_service, name_id, "HAUT", 7.0)
    
    # --- 3. RESET POSTURE AVANT ROTATION ---
    print("🔄 Retour posture stable...")
    # On remet les hanches à 0 d'abord !
    motion.setAngles(["LHipPitch", "RHipPitch"], [0.0, 0.0], 0.03)
    motion.setAngles("HeadPitch", -0.1, 0.1)
    motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.03)
    
    # On attend que le reset soit fini avant de tourner
    time.sleep(1.0) 
    
    # --- 4. ROTATION ---
    print("🔄 Rotation...")
    motion.moveTo(0, 0, 1.0)

def autonomous_exploration(session, img, video_service, name_id):
    """Cerveau principal appelé pour chaque image reçue."""
    global yolo_model, visited_zones
    
    motion = session.service("ALMotion")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")

    # 1. CHARGEMENT UNIQUE DU MODÈLE
    if yolo_model is None:
        yolo_model = YOLO(MODEL_PATH)

    # 2. GESTION DES OBSTACLES (SONARS)
    left = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    right = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
    
    if left < 0.45 or right < 0.45:
        motion.stopMove()
        motion.moveTo(-0.1, 0, 0)
        motion.moveTo(0, 0, 0.6 if left < right else -0.6)
        return 

    # 3. DÉTECTION HUMAINE
    person_detected, annotated_img = detect_person(img, yolo_model)
    cv2.imshow("Exploration Robot", annotated_img)

    if person_detected:
        # On arrête tout mouvement en cours
        motion.stopMove()
        
        # On lance le scan ET la rotation (qui sont bloquants dans perform_vertical_scan)
        perform_vertical_scan(session, video_service, name_id)
        
        # IMPORTANT : On sort de la fonction ici pour que la boucle connexionCamera 
        # reprenne proprement sans exécuter le motion.move() du bas.
        return 

    # 4. SLAM (Logique de visite des zones)
    x, z = get_slam_position() 
    if x != 0.0 or z != 0.0:
        cx, cz = int(round(x/0.5)), int(round(z/0.5))
        if (cx, cz) not in visited_zones:
            visited_zones.add((cx, cz))
            if len(visited_zones) >= 30:
                motion.stopMove()
                tts.say("Exploration terminée.")
                return

    # 5. MARCHE PAR DÉFAUT (si rien n'est détecté)
    motion.move(0.08, 0, 0)