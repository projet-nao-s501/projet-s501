#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Menu Complet NAO - Projet S501
==============================

Menu interactif pour contrôler le robot NAO avec :
- Reconnaissance d'objets en temps réel
- Navigation intelligente avec sonar
- Cartographie SLAM de la salle
- Contrôles de posture et mouvements

Fonctionnalités:
1. Reconnaissance objets avec caméra 
2. Scan vertical 3 crans (pieds/torse/tête)
3. Scan horizontal de la tête
4. Scan vertical de la tête  
5. Reset regard à l'horizon
6. Navigation avec sonar (NOUVEAU)
7. Exploration intelligente (NOUVEAU)
8. Test équilibre gyroscopes
9. Faire lever le robot
10. Faire asseoir le robot
0. Quitter

Auteur: Assistant IA
Version: 2.0
"""

import argparse
import sys
import time
import threading
import numpy as np
import cv2
import os
from collections import deque
import json
from datetime import datetime

# Import conditionnel pour compatibilité
try:
    import qi
    QI_AVAILABLE = True
except ImportError:
    QI_AVAILABLE = False
    print("⚠️ Module 'qi' non disponible - Mode démo activé")

try:
    from keras.models import load_model
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️ Module 'keras' non disponible - Reconnaissance désactivée")

class NAOController:
    """Contrôleur principal pour le robot NAO"""
    
    def __init__(self, session):
        self.session = session
        self.is_demo = not QI_AVAILABLE or session is None
        
        # Initialisation des services NAO
        if not self.is_demo:
            try:
                self.motion = session.service("ALMotion")
                self.posture = session.service("ALRobotPosture") 
                self.video = session.service("ALVideoDevice")
                self.memory = session.service("ALMemory")
                self.sonar = session.service("ALSonar")
                self.head_motion = session.service("ALMotion")
                
                print("✅ Services NAO initialisés")
            except Exception as e:
                print(f"⚠️ Erreur services NAO: {e}")
                self.is_demo = True
        
        if self.is_demo:
            print("🎮 Mode DEMO activé")
            
        # Système de navigation intelligente
        from nao_navigation import IntelligentNavigation
        self.navigation_system = IntelligentNavigation(session)
        
        # Variables de reconnaissance
        self.model = None
        self.class_names = None
        self.camera_subscriber = None
        
    def load_recognition_model(self):
        """Charge le modèle de reconnaissance d'objets"""
        if not KERAS_AVAILABLE:
            print("❌ Keras non disponible - Reconnaissance impossible")
            return False
            
        try:
            # Tentative de chargement du modèle
            if os.path.exists("keras_model.h5"):
                self.model = load_model("keras_model.h5", compile=False)
                print("✅ Modèle Keras chargé")
            else:
                print("⚠️ Fichier keras_model.h5 non trouvé")
                return False
                
            if os.path.exists("labels.txt"):
                self.class_names = open("labels.txt", "r").readlines()
                print(f"✅ Labels chargés ({len(self.class_names)} classes)")
            else:
                print("⚠️ Fichier labels.txt non trouvé") 
                return False
                
            return True
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            return False

    def wake_up_robot(self):
        """Réveille et initialise le robot"""
        if self.is_demo:
            print("🎮 [DEMO] Robot réveillé et prêt")
            return True
            
        try:
            print("🤖 Réveil du robot...")
            self.motion.wakeUp()
            time.sleep(2)
            
            print("🚶 Position debout...")
            self.posture.goToPosture("StandInit", 1.0)
            
            print("✅ Robot prêt!")
            return True
        except Exception as e:
            print(f"❌ Erreur réveil robot: {e}")
            return False

    def reconnaissance_objets(self):
        """1. Reconnaissance d'objets en temps réel"""
        print("\n" + "="*50)
        print("📷 RECONNAISSANCE D'OBJETS EN TEMPS RÉEL")
        print("="*50)
        
        if not self.load_recognition_model():
            print("❌ Impossible de charger le modèle de reconnaissance")
            return
            
        if self.is_demo:
            print("🎮 [DEMO] Mode simulation reconnaissance")
            for i in range(5):
                print(f"   Frame {i+1}: Objet détecté - Confiance: {85+i}%")
                time.sleep(1)
            return
            
        try:
            # Configuration caméra
            resolution = 2  # VGA 640x480
            color_space = 11  # RGB
            fps = 15
            camera_index = 1
            
            # Abonnement caméra
            self.camera_subscriber = self.video.subscribeCamera("", camera_index, resolution, color_space, fps)
            print(f"✅ Caméra connectée: {self.camera_subscriber}")
            
            print("🎬 Démarrage reconnaissance - Appuyez sur 'q' pour quitter")
            
            while True:
                # Récupération image
                image = self.video.getImageRemote(self.camera_subscriber)
                if image is None:
                    continue
                    
                width, height = image[0], image[1]
                array = image[6]
                img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
                
                # Conversion pour OpenCV
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                cv2.imshow("NAO - Reconnaissance Objets", img_bgr)
                
                # Prédiction avec le modèle
                img_resized = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
                img_array = np.asarray(img_resized, dtype=np.float32).reshape(1, 224, 224, 3)
                img_normalized = (img_array / 127.5) - 1
                
                prediction = self.model.predict(img_array)
                index = np.argmax(prediction)
                class_name = self.class_names[index].strip()
                confidence = prediction[0][index] * 100
                
                print(f"🔍 Objet: {class_name} - Confiance: {confidence:.1f}%")
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"❌ Erreur reconnaissance: {e}")
        finally:
            if self.camera_subscriber:
                self.video.unsubscribe(self.camera_subscriber)
            cv2.destroyAllWindows()
            print("✅ Reconnaissance arrêtée")

    def scan_vertical_personne(self):
        """2. Scan vertical 3 crans (pieds/torse/tête)"""
        print("\n" + "="*50)  
        print("👥 SCAN VERTICAL PERSONNE (3 CRANS)")
        print("="*50)
        
        if self.is_demo:
            positions = ["Pieds", "Torse", "Tête"]
            for pos in positions:
                print(f"🎮 [DEMO] Scan {pos}...")
                time.sleep(2)
            return
            
        try:
            # Positions de tête pour scanner une personne debout
            positions = [
                ("Pieds", -0.5, 0.0),    # Regarder vers le bas
                ("Torse", -0.1, 0.0),    # Regarder droit devant  
                ("Tête", 0.3, 0.0)       # Regarder vers le haut
            ]
            
            for name, pitch, yaw in positions:
                print(f"👀 Scan {name}...")
                self.head_motion.setAngles(["HeadPitch", "HeadYaw"], [pitch, yaw], 0.3)
                time.sleep(3)  # Temps pour l'analyse
                
            print("✅ Scan vertical terminé")
            
        except Exception as e:
            print(f"❌ Erreur scan vertical: {e}")

    def scan_horizontal_tete(self):
        """3. Scan horizontal de la tête"""
        print("\n" + "="*50)
        print("🔄 SCAN HORIZONTAL DE LA TÊTE") 
        print("="*50)
        
        if self.is_demo:
            directions = ["Gauche", "Centre", "Droite", "Centre"]
            for direction in directions:
                print(f"🎮 [DEMO] Regard {direction}...")
                time.sleep(1.5)
            return
            
        try:
            # Positions horizontales (yaw seulement)
            positions = [
                ("Gauche", 0.0, 1.0),     # Tourner à gauche
                ("Centre", 0.0, 0.0),     # Revenir au centre
                ("Droite", 0.0, -1.0),    # Tourner à droite  
                ("Centre", 0.0, 0.0)      # Revenir au centre
            ]
            
            for name, pitch, yaw in positions:
                print(f"👀 Regard {name}...")
                self.head_motion.setAngles(["HeadPitch", "HeadYaw"], [pitch, yaw], 0.2)
                time.sleep(2)
                
            print("✅ Scan horizontal terminé")
            
        except Exception as e:
            print(f"❌ Erreur scan horizontal: {e}")

    def scan_vertical_tete(self):
        """4. Scan vertical de la tête"""
        print("\n" + "="*50)
        print("⬆️ SCAN VERTICAL DE LA TÊTE")
        print("="*50)
        
        if self.is_demo:
            directions = ["Haut", "Centre", "Bas", "Centre"]
            for direction in directions:
                print(f"🎮 [DEMO] Regard {direction}...")
                time.sleep(1.5)
            return
            
        try:
            # Positions verticales (pitch seulement)
            positions = [
                ("Haut", 0.4, 0.0),       # Regarder vers le haut
                ("Centre", 0.0, 0.0),     # Position neutre
                ("Bas", -0.4, 0.0),       # Regarder vers le bas
                ("Centre", 0.0, 0.0)      # Revenir au centre
            ]
            
            for name, pitch, yaw in positions:
                print(f"👀 Regard {name}...")
                self.head_motion.setAngles(["HeadPitch", "HeadYaw"], [pitch, yaw], 0.2)
                time.sleep(2)
                
            print("✅ Scan vertical tête terminé")
            
        except Exception as e:
            print(f"❌ Erreur scan vertical: {e}")

    def reset_regard_horizon(self):
        """5. Reset du regard à l'horizon"""
        print("\n" + "="*50)
        print("🎯 RESET REGARD À L'HORIZON")
        print("="*50)
        
        if self.is_demo:
            print("🎮 [DEMO] Regard remis à l'horizon")
            return
            
        try:
            print("🔄 Remise à zéro du regard...")
            # Position neutre: tête droite, regard à l'horizon
            self.head_motion.setAngles(["HeadPitch", "HeadYaw"], [0.0, 0.0], 0.3)
            time.sleep(2)
            print("✅ Regard repositionné à l'horizon")
            
        except Exception as e:
            print(f"❌ Erreur reset regard: {e}")

    def navigation_avec_sonar(self):
        """6. Navigation avec sonar (NOUVEAU)"""
        print("\n" + "="*50)
        print("🚶 NAVIGATION AVEC SONAR")
        print("="*50)
        
        if self.is_demo:
            print("🎮 [DEMO] Simulation navigation avec sonar")
            for i in range(3):
                print(f"   Étape {i+1}: Marche... Sonar: {0.8+i*0.3:.1f}m")
                time.sleep(2)
            print("   Obstacle détecté! Arrêt.")
            return
            
        try:
            # Utilisation du système de navigation
            navigator = self.navigation_system.navigator
            
            print("🚀 Démarrage navigation avec détection sonar")
            print("   Distance cible: 2.0m")
            print("   Seuil obstacle: 0.5m")
            
            success = navigator.move_forward_with_sonar(distance=2.0, speed=0.3)
            
            if success:
                print("✅ Navigation terminée avec succès")
            else:
                print("⚠️ Navigation arrêtée - Obstacle détecté")
                
        except Exception as e:
            print(f"❌ Erreur navigation: {e}")

    def exploration_intelligente(self):
        """7. Exploration intelligente (NOUVEAU)"""
        print("\n" + "="*50)
        print("🗺️ EXPLORATION INTELLIGENTE DE LA SALLE")
        print("="*50)
        
        print("🚀 Démarrage de l'exploration autonome...")
        print("   - Cartographie SLAM en temps réel")
        print("   - Évitement des boucles infinies") 
        print("   - Détection d'obstacles par sonar")
        print("   - Visualisation de la carte")
        
        try:
            # Démarrage du système d'exploration
            self.navigation_system.start_intelligent_exploration()
            
            print("\n⌨️ Contrôles disponibles:")
            print("   - Entrée: Continuer l'exploration")
            print("   - 'stop' + Entrée: Arrêter l'exploration")
            print("   - 'q' + Entrée: Quitter")
            
            while self.navigation_system.is_active:
                user_input = input("\n> ").strip().lower()
                
                if user_input in ['q', 'quit', 'exit']:
                    break
                elif user_input in ['stop', 'arrêt', 'arret']:
                    self.navigation_system.stop_intelligent_exploration()
                    break
                    
            if self.navigation_system.is_active:
                self.navigation_system.stop_intelligent_exploration()
                
        except Exception as e:
            print(f"❌ Erreur exploration: {e}")

    def test_equilibre_gyroscopes(self):
        """8. Test équilibre via gyroscopes"""
        print("\n" + "="*50)
        print("⚖️ TEST D'ÉQUILIBRE GYROSCOPES")
        print("="*50)
        
        if self.is_demo:
            print("🎮 [DEMO] Lecture gyroscopes simulée")
            for i in range(5):
                x = np.random.uniform(-0.1, 0.1)
                y = np.random.uniform(-0.1, 0.1) 
                print(f"   Gyro X: {x:.3f} rad/s, Y: {y:.3f} rad/s - {'✅ Équilibré' if abs(x)<0.05 and abs(y)<0.05 else '⚠️ Déséquilibré'}")
                time.sleep(1)
            return
            
        try:
            print("📊 Lecture des capteurs gyroscopiques...")
            
            for i in range(10):
                # Lecture des gyroscopes  
                gyr_x = self.memory.getData("Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value")
                gyr_y = self.memory.getData("Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value")
                gyr_z = self.memory.getData("Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value")
                
                # Lecture accéléromètres
                acc_x = self.memory.getData("Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value")
                acc_y = self.memory.getData("Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value")
                acc_z = self.memory.getData("Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value")
                
                print(f"🔄 Étape {i+1}:")
                print(f"   Gyroscope: X={gyr_x:.3f} Y={gyr_y:.3f} Z={gyr_z:.3f} rad/s")
                print(f"   Accéléromètre: X={acc_x:.3f} Y={acc_y:.3f} Z={acc_z:.3f} m/s²")
                
                # Analyse de l'équilibre
                if abs(gyr_x) < 0.1 and abs(gyr_y) < 0.1:
                    print("   Status: ✅ Robot équilibré")
                else:
                    print("   Status: ⚠️ Robot déséquilibré")
                
                time.sleep(1)
                
            print("✅ Test gyroscopes terminé")
            
        except Exception as e:
            print(f"❌ Erreur test gyroscopes: {e}")

    def faire_lever_robot(self):
        """9. Faire lever le robot"""
        print("\n" + "="*50)
        print("🚶 FAIRE LEVER LE ROBOT")
        print("="*50)
        
        if self.is_demo:
            print("🎮 [DEMO] Robot en train de se lever...")
            time.sleep(3)
            print("✅ Robot debout!")
            return
            
        try:
            print("🤖 Le robot se lève...")
            
            # Vérification de l'état actuel
            current_posture = self.posture.getPosture()
            print(f"Position actuelle: {current_posture}")
            
            if current_posture in ["Sit", "SitRelax", "Crouch"]:
                # Se lever depuis une position assise
                self.posture.goToPosture("Stand", 1.0)
                print("✅ Robot levé depuis position assise")
            elif current_posture in ["LyingBack", "LyingBelly"]:
                # Se lever depuis position couchée
                self.posture.goToPosture("Stand", 2.0)  # Plus de temps
                print("✅ Robot levé depuis position couchée")
            else:
                print("ℹ️ Robot déjà debout")
                
        except Exception as e:
            print(f"❌ Erreur lever robot: {e}")

    def faire_asseoir_robot(self):
        """10. Faire asseoir le robot"""
        print("\n" + "="*50)
        print("🪑 FAIRE ASSEOIR LE ROBOT")
        print("="*50)
        
        if self.is_demo:
            print("🎮 [DEMO] Robot en train de s'asseoir...")
            time.sleep(3)
            print("✅ Robot assis!")
            return
            
        try:
            print("🤖 Le robot s'assoit...")
            
            # Position assise
            self.posture.goToPosture("Sit", 1.0)
            
            print("✅ Robot assis")
            
        except Exception as e:
            print(f"❌ Erreur asseoir robot: {e}")

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("🤖 MENU COMPLET ROBOT NAO - PROJET S501")
    print("="*60)
    print("1. 📷 Reconnaissance d'objets (caméra + IA)")
    print("2. 👥 Scan vertical personne (pieds/torse/tête)")  
    print("3. 🔄 Scan horizontal de la tête")
    print("4. ⬆️ Scan vertical de la tête")
    print("5. 🎯 Reset regard à l'horizon")
    print("6. 🚶 Navigation avec sonar (NOUVEAU)")
    print("7. 🗺️ Exploration intelligente (NOUVEAU)")
    print("8. ⚖️ Test équilibre gyroscopes")
    print("9. 🚶 Faire lever le robot")
    print("10.🪑 Faire asseoir le robot")
    print("0. ❌ Quitter")
    print("="*60)

def main(session):
    """Fonction principale avec menu interactif"""
    
    print("\n" + "🤖"*20)
    print("BIENVENUE DANS LE SYSTÈME NAO COMPLET")
    print("🤖"*20 + "\n")
    
    # Initialisation du contrôleur
    controller = NAOController(session)
    
    # Réveil du robot
    if not controller.wake_up_robot():
        print("❌ Impossible d'initialiser le robot")
        return
    
    # Boucle principale du menu
    while True:
        afficher_menu()
        
        try:
            choix = input("👉 Votre choix (0-10): ").strip()
            
            if choix == "0":
                print("👋 Au revoir!")
                break
            elif choix == "1":
                controller.reconnaissance_objets()
            elif choix == "2":
                controller.scan_vertical_personne()
            elif choix == "3": 
                controller.scan_horizontal_tete()
            elif choix == "4":
                controller.scan_vertical_tete()
            elif choix == "5":
                controller.reset_regard_horizon()
            elif choix == "6":
                controller.navigation_avec_sonar()
            elif choix == "7":
                controller.exploration_intelligente()
            elif choix == "8":
                controller.test_equilibre_gyroscopes()
            elif choix == "9":
                controller.faire_lever_robot()
            elif choix == "10":
                controller.faire_asseoir_robot()
            else:
                print("❌ Choix invalide. Utilisez 0-10.")
                
            # Pause entre les actions
            if choix != "0":
                input("\n⏸️ Appuyez sur Entrée pour continuer...")
                
        except KeyboardInterrupt:
            print("\n🛑 Interruption clavier - Arrêt du programme")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    # Nettoyage final
    if not controller.is_demo:
        try:
            print("😴 Mise en veille du robot...")
            controller.motion.rest()
        except:
            pass
    
    print("🏁 Fin du programme")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Menu Complet NAO - Projet S501")
    parser.add_argument("--ip", type=str, default="172.16.1.164",
                        help="Adresse IP du robot NAO")
    parser.add_argument("--port", type=int, default=9559,
                        help="Port Naoqi")
    parser.add_argument("--demo", action="store_true",
                        help="Mode démonstration (sans robot)")

    args = parser.parse_args()
    
    print(f"\n🔗 Tentative de connexion à {args.ip}:{args.port}")
    
    if args.demo or not QI_AVAILABLE:
        print("🎮 Mode DÉMONSTRATION")
        main(None)
    else:
        session = qi.Session()
        try:
            session.connect("tcp://" + args.ip + ":" + str(args.port))
            print("✅ Connexion NAO réussie!")
            main(session)
        except RuntimeError as e:
            print(f"❌ Connexion échouée: {e}")
            print("💡 Vérifiez:")
            print("   - Robot NAO allumé") 
            print("   - Même réseau")
            print("   - Adresse IP correcte")
            print("\n🎮 Passage en mode DÉMONSTRATION...")
            main(None)