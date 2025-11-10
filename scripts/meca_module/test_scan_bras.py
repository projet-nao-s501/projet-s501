#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Script de test pour l'option 5 - Scan vertical avec bras
Test isolé pour déboguer
"""

import qi
import sys
import time
import json

def load_config():
    """Charge la configuration depuis config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config['robot_ip'], config['robot_port']
    except Exception as e:
        print(f"Erreur config: {e}")
        return "172.16.1.163", 9559

def test_scan_avec_bras():
    """Test du scan vertical avec bras"""
    robot_ip, robot_port = load_config()
    
    print(f"\n=== TEST SCAN AVEC BRAS ===")
    print(f"Connexion à {robot_ip}:{robot_port}...")
    
    session = qi.Session()
    try:
        session.connect(f"tcp://{robot_ip}:{robot_port}")
        print("✓ Connexion réussie!\n")
    except Exception as e:
        print(f"✗ Erreur connexion: {e}")
        sys.exit(1)
    
    try:
        motion = session.service("ALMotion")
        
        print("PHASE 1: Activation des moteurs")
        print("  → Activation de la tête et des bras...")
        motion.setStiffnesses(["Head", "LArm", "RArm"], 1.0)
        time.sleep(1)
        print("  ✓ Moteurs actifs\n")
        
        print("PHASE 2: Positionnement des bras")
        print("  → Bras vers l'avant...")
        
        names = ["LShoulderPitch", "LShoulderRoll", "RShoulderPitch", "RShoulderRoll"]
        angles = [0.8, 0.15, 0.8, -0.15]
        speed = 0.15
        
        motion.setAngles(names, angles, speed)
        time.sleep(2)
        print("  ✓ Bras en position\n")
        
        print("PHASE 3: Scan de la tête")
        positions = [
            ("Très haut", -0.50),
            ("Tête", -0.30),
            ("Poitrine", -0.10),
            ("Torse", 0.15)
        ]
        
        for i, (nom, pitch) in enumerate(positions, 1):
            print(f"  → Position {i}/4: {nom} (pitch: {pitch:.2f})")
            motion.setAngles("HeadPitch", pitch, 0.15)
            time.sleep(4)
        
        print("\n  ✓ Scan terminé\n")
        
        print("PHASE 4: Retour à la normale")
        print("  → Tête au centre...")
        motion.setAngles("HeadPitch", 0.0, 0.15)
        time.sleep(1.5)
        
        print("  → Bras le long du corps...")
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.15)
        motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.1, -0.1], 0.15)
        time.sleep(2)
        
        print("  ✓ Position normale\n")
        
        print("✅ TEST RÉUSSI !")
        print("\nL'option 5 devrait fonctionner correctement dans le menu.")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("\nDétails de l'erreur:")
        import traceback
        traceback.print_exc()
        
        print("\n📋 Suggestions:")
        print("  1. Vérifiez que le robot est en position DEBOUT")
        print("  2. Vérifiez que les batteries sont chargées")
        print("  3. Essayez de redémarrer le robot")
    
    print("\nTest terminé.")

if __name__ == "__main__":
    test_scan_avec_bras()
