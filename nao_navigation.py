#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Module de Navigation Intelligente pour NAO
==========================================

Fonctionnalités:
1. Marche avec détection sonar et arrêt automatique
2. Système de cartographie SLAM (Simultaneous Localization And Mapping)
3. Navigation intelligente évitant les boucles infinies
4. Visualisation en temps réel de la carte

Auteur: Assistant IA
Version: 1.0
"""

import argparse
import sys
import time
import threading
import numpy as np
import os
from collections import deque
import json
from datetime import datetime

# Import conditionnel pour mode démo
try:
    import qi
    QI_AVAILABLE = True
except ImportError:
    QI_AVAILABLE = False
    print("⚠️ Module 'qi' non disponible - Mode démo activé")

class RoomMapper:
    """Gestionnaire de cartographie intelligente de la salle"""
    
    def __init__(self, width=50, height=50, resolution=0.1):
        """
        Initialise la carte de la salle
        
        Args:
            width (int): Largeur de la carte en cellules
            height (int): Hauteur de la carte en cellules  
            resolution (float): Résolution en mètres par cellule
        """
        self.width = width
        self.height = height
        self.resolution = resolution  # mètres par cellule
        
        # Matrice de la salle
        # 0 = libre, 1 = obstacle, 2 = exploré, -1 = inconnu
        self.grid = np.full((height, width), -1, dtype=np.int8)
        
        # Position du robot (centre de la carte au début)
        self.robot_x = width // 2
        self.robot_y = height // 2
        self.robot_heading = 0.0  # angle en radians
        
        # Historique des positions visitées
        self.visited_positions = set()
        self.path_history = deque(maxlen=1000)
        
        # Statistiques
        self.obstacles_detected = 0
        self.cells_explored = 0
        
        # Marquer la position initiale comme libre
        self.grid[self.robot_y, self.robot_x] = 2
        self.visited_positions.add((self.robot_x, self.robot_y))
        
    def update_position(self, delta_x, delta_y, heading):
        """Met à jour la position du robot"""
        # Conversion des déplacements réels vers coordonnées de grille
        grid_delta_x = int(delta_x / self.resolution)
        grid_delta_y = int(delta_y / self.resolution)
        
        new_x = max(0, min(self.width-1, self.robot_x + grid_delta_x))
        new_y = max(0, min(self.height-1, self.robot_y + grid_delta_y))
        
        self.robot_x = new_x
        self.robot_y = new_y
        self.robot_heading = heading
        
        # Marquer comme exploré
        if self.grid[new_y, new_x] == -1:
            self.grid[new_y, new_x] = 2
            self.cells_explored += 1
            
        self.visited_positions.add((new_x, new_y))
        self.path_history.append((new_x, new_y, time.time()))
        
    def add_obstacle(self, distance, angle):
        """Ajoute un obstacle détecté par le sonar"""
        # Calcul de la position de l'obstacle
        abs_angle = self.robot_heading + angle
        obstacle_x = self.robot_x + int((distance * np.cos(abs_angle)) / self.resolution)
        obstacle_y = self.robot_y + int((distance * np.sin(abs_angle)) / self.resolution)
        
        # Vérification des limites
        if 0 <= obstacle_x < self.width and 0 <= obstacle_y < self.height:
            self.grid[obstacle_y, obstacle_x] = 1
            self.obstacles_detected += 1
            
    def get_best_direction(self):
        """Retourne la meilleure direction à prendre (évite les boucles)"""
        directions = [
            (0, -1, "Nord"),      # Haut
            (1, 0, "Est"),        # Droite  
            (0, 1, "Sud"),        # Bas
            (-1, 0, "Ouest")      # Gauche
        ]
        
        best_score = -1
        best_direction = None
        best_name = ""
        
        for dx, dy, name in directions:
            new_x = self.robot_x + dx
            new_y = self.robot_y + dy
            
            # Vérification des limites
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                continue
                
            # Si c'est un obstacle, ignorer
            if self.grid[new_y, new_x] == 1:
                continue
                
            # Calcul du score (priorité aux zones inexplorées)
            score = 0
            
            # Bonus pour les zones inexplorées
            if self.grid[new_y, new_x] == -1:
                score += 100
                
            # Malus pour les zones déjà visitées récemment
            visit_count = sum(1 for pos in list(self.path_history)[-20:] 
                            if pos[0] == new_x and pos[1] == new_y)
            score -= visit_count * 10
            
            # Bonus pour s'éloigner du centre si on y est depuis longtemps
            center_distance = abs(new_x - self.width//2) + abs(new_y - self.height//2)
            if len(self.path_history) > 10:
                recent_positions = [pos[:2] for pos in list(self.path_history)[-10:]]
                if recent_positions.count((self.robot_x, self.robot_y)) > 5:
                    score += center_distance * 5
                    
            if score > best_score:
                best_score = score
                best_direction = (dx, dy)
                best_name = name
                
        return best_direction, best_name, best_score
    
    def display_map(self):
        """Affiche la carte dans le terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "=" * 60)
        print("🗺️  CARTE DE LA SALLE - NAO NAVIGATION")
        print("=" * 60)
        
        symbols = {
            -1: "?",  # Inexploré
            0: ".",   # Libre
            1: "█",   # Obstacle
            2: "·"    # Exploré
        }
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if x == self.robot_x and y == self.robot_y:
                    # Position du robot avec direction
                    if -0.785 < self.robot_heading <= 0.785:  # Est
                        row += "→"
                    elif 0.785 < self.robot_heading <= 2.356:  # Sud
                        row += "↓"
                    elif 2.356 < self.robot_heading <= 3.927:  # Ouest
                        row += "←"
                    else:  # Nord
                        row += "↑"
                else:
                    row += symbols.get(self.grid[y, x], "?")
            print(f"{y:2d} |{row}|")
            
        print("   " + "+" + "-" * self.width + "+")
        
        # Légende et statistiques
        print(f"\n📊 STATISTIQUES:")
        print(f"   🤖 Position: ({self.robot_x}, {self.robot_y})")
        print(f"   🧭 Direction: {self.robot_heading:.2f} rad ({np.degrees(self.robot_heading):.1f}°)")
        print(f"   🔍 Cellules explorées: {self.cells_explored}")
        print(f"   🚧 Obstacles détectés: {self.obstacles_detected}")
        print(f"   👣 Positions visitées: {len(self.visited_positions)}")
        
        print(f"\n🗺️  LÉGENDE:")
        print(f"   ? = Inexploré  · = Exploré  █ = Obstacle  . = Libre")
        print(f"   ↑↓←→ = Robot NAO")

class SonarNavigator:
    """Gestionnaire de navigation avec sonar"""
    
    def __init__(self, session):
        self.session = session
        self.is_moving = False
        self.stop_requested = False
        
        # Services NAO
        if QI_AVAILABLE and session:
            try:
                self.motion = session.service("ALMotion")
                self.memory = session.service("ALMemory")
                self.sonar = session.service("ALSonar")
                self.posture = session.service("ALRobotPosture")
                
                # Activation des sonars
                self.sonar.subscribe("NavigationSonar")
                print("✅ Services NAO initialisés")
            except Exception as e:
                print(f"⚠️ Erreur services NAO: {e}")
                self.motion = None
        else:
            self.motion = None
            print("🎮 Mode DEMO - Navigation simulée")
        
        # Seuils de détection
        self.OBSTACLE_DISTANCE = 0.5  # 50cm
        self.SAFE_DISTANCE = 0.3      # 30cm
        
    def get_sonar_values(self):
        """Récupère les valeurs des capteurs sonar"""
        if not self.motion:
            # Mode démo - simulation de valeurs sonar
            import random
            left = random.uniform(0.2, 2.5)
            right = random.uniform(0.2, 2.5)
            return left, right
            
        try:
            # Sonars NAO réels
            left = self.memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            right = self.memory.getData("Device/SubDeviceList/US/Right/Sensor/Value") 
            return left, right
        except Exception as e:
            print(f"Erreur sonar: {e}")
            return 2.5, 2.5  # Valeurs par défaut
    
    def move_forward_with_sonar(self, distance=0.5, speed=0.5):
        """
        Avance avec détection d'obstacles par sonar
        
        Args:
            distance (float): Distance à parcourir (mètres)
            speed (float): Vitesse de déplacement (0.0 à 1.0)
        """
        if not self.motion:
            print("🎮 [DEMO] Simulation marche avec sonar")
            time.sleep(2)
            return True
            
        print(f"🚶 Début de marche: {distance}m à vitesse {speed}")
        
        self.is_moving = True
        self.stop_requested = False
        
        try:
            # Position initiale
            initial_pos = self.motion.getRobotPosition(True)
            target_distance = distance
            moved_distance = 0.0
            
            # Démarrer le mouvement
            self.motion.moveToward(speed, 0.0, 0.0)
            
            while moved_distance < target_distance and not self.stop_requested:
                # Vérification des sonars
                left_sonar, right_sonar = self.get_sonar_values()
                
                print(f"🔍 Sonar L:{left_sonar:.2f}m R:{right_sonar:.2f}m - Distance:{moved_distance:.2f}m/{target_distance:.2f}m")
                
                # Détection d'obstacle
                if left_sonar < self.OBSTACLE_DISTANCE or right_sonar < self.OBSTACLE_DISTANCE:
                    print(f"🚧 OBSTACLE DÉTECTÉ! L:{left_sonar:.2f}m R:{right_sonar:.2f}m")
                    break
                
                # Calcul de la distance parcourue
                current_pos = self.motion.getRobotPosition(True)
                moved_distance = np.sqrt((current_pos[0] - initial_pos[0])**2 + 
                                       (current_pos[1] - initial_pos[1])**2)
                
                time.sleep(0.1)
            
            # Arrêt du mouvement
            self.motion.stopMove()
            self.is_moving = False
            
            final_pos = self.motion.getRobotPosition(True)
            actual_distance = np.sqrt((final_pos[0] - initial_pos[0])**2 + 
                                    (final_pos[1] - initial_pos[1])**2)
            
            print(f"✅ Marche terminée - Distance réelle: {actual_distance:.2f}m")
            return actual_distance > 0.1  # Succès si on a bougé d'au moins 10cm
            
        except Exception as e:
            print(f"❌ Erreur pendant la marche: {e}")
            if self.motion:
                self.motion.stopMove()
            self.is_moving = False
            return False
    
    def stop_movement(self):
        """Arrête immédiatement le mouvement"""
        self.stop_requested = True
        if self.motion and self.is_moving:
            self.motion.stopMove()
            print("🛑 Mouvement arrêté")

class IntelligentNavigation:
    """Système complet de navigation intelligente"""
    
    def __init__(self, session):
        self.session = session
        self.mapper = RoomMapper(width=40, height=40, resolution=0.1)
        self.navigator = SonarNavigator(session)
        
        self.is_active = False
        self.navigation_thread = None
        
    def start_intelligent_exploration(self):
        """Démarre l'exploration intelligente de la salle"""
        if self.is_active:
            print("⚠️ Navigation déjà active")
            return
            
        print("🚀 DÉMARRAGE DE L'EXPLORATION INTELLIGENTE")
        print("=" * 50)
        
        self.is_active = True
        self.navigation_thread = threading.Thread(target=self._exploration_loop)
        self.navigation_thread.daemon = True
        self.navigation_thread.start()
        
    def stop_intelligent_exploration(self):
        """Arrête l'exploration intelligente"""
        print("🛑 Arrêt de l'exploration demandé...")
        self.is_active = False
        self.navigator.stop_movement()
        
        if self.navigation_thread and self.navigation_thread.is_alive():
            self.navigation_thread.join(timeout=5)
            
        print("✅ Exploration arrêtée")
        
    def _exploration_loop(self):
        """Boucle principale d'exploration"""
        step_count = 0
        
        try:
            while self.is_active:
                step_count += 1
                print(f"\n🚶 ÉTAPE {step_count} - Exploration intelligente")
                
                # Mise à jour de l'affichage
                self.mapper.display_map()
                
                # Récupération des données sonar
                left_sonar, right_sonar = self.navigator.get_sonar_values()
                print(f"🔍 Capteurs: Sonar L={left_sonar:.2f}m R={right_sonar:.2f}m")
                
                # Ajout des obstacles détectés à la carte
                if left_sonar < 1.0:  # Obstacle à moins d'1m à gauche
                    self.mapper.add_obstacle(left_sonar, -np.pi/4)  # -45°
                if right_sonar < 1.0:  # Obstacle à moins d'1m à droite  
                    self.mapper.add_obstacle(right_sonar, np.pi/4)   # +45°
                
                # Calcul de la meilleure direction
                direction, direction_name, score = self.mapper.get_best_direction()
                
                if direction is None:
                    print("🤔 Aucune direction libre trouvée - Arrêt")
                    break
                    
                print(f"🧭 Meilleure direction: {direction_name} (score: {score})")
                
                # Rotation vers la direction choisie (simulée)
                target_angle = np.arctan2(direction[1], direction[0])
                if not QI_AVAILABLE:
                    print(f"🎮 [DEMO] Rotation vers {direction_name} ({np.degrees(target_angle):.1f}°)")
                    time.sleep(1)
                
                # Tentative de déplacement
                success = self.navigator.move_forward_with_sonar(distance=0.3, speed=0.3)
                
                if success:
                    # Mise à jour de la position
                    delta_x = direction[0] * 0.3  # 30cm dans la direction
                    delta_y = direction[1] * 0.3
                    self.mapper.update_position(delta_x, delta_y, target_angle)
                    print(f"✅ Déplacement réussi vers {direction_name}")
                else:
                    print(f"⚠️ Déplacement bloqué - Obstacle détecté")
                    # Marquer la direction comme obstruée
                    obs_x = self.mapper.robot_x + direction[0]
                    obs_y = self.mapper.robot_y + direction[1]
                    if 0 <= obs_x < self.mapper.width and 0 <= obs_y < self.mapper.height:
                        self.mapper.grid[obs_y, obs_x] = 1
                
                # Pause entre les étapes
                time.sleep(2)
                
                # Condition d'arrêt: trop de cellules explorées
                if self.mapper.cells_explored > 200:
                    print("🏁 Exploration complète - Arrêt automatique")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Exploration interrompue par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur pendant l'exploration: {e}")
        finally:
            self.is_active = False
            print("\n📊 Exploration terminée!")
            self.mapper.display_map()
            self._save_exploration_data()
    
    def _save_exploration_data(self):
        """Sauvegarde les données d'exploration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nao_exploration_{timestamp}.json"
        
        data = {
            "timestamp": timestamp,
            "grid": self.mapper.grid.tolist(),
            "robot_position": [self.mapper.robot_x, self.mapper.robot_y],
            "statistics": {
                "cells_explored": self.mapper.cells_explored,
                "obstacles_detected": self.mapper.obstacles_detected,
                "positions_visited": len(self.mapper.visited_positions)
            },
            "path_history": list(self.mapper.path_history)
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données sauvées: {filename}")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde: {e}")

def demo_navigation():
    """Démonstration du système de navigation"""
    print("🎮 DÉMONSTRATION - Navigation Intelligente NAO")
    print("=" * 50)
    
    nav_system = IntelligentNavigation(None)  # Mode démo
    
    try:
        nav_system.start_intelligent_exploration()
        
        print("\n⌨️ Contrôles disponibles:")
        print("   - Entrée: Continuer l'exploration")  
        print("   - 'q' + Entrée: Quitter")
        
        while nav_system.is_active:
            user_input = input("\n> ").strip().lower()
            if user_input in ['q', 'quit', 'exit']:
                nav_system.stop_intelligent_exploration()
                break
                
    except KeyboardInterrupt:
        nav_system.stop_intelligent_exploration()
    
    print("🏁 Fin de la démonstration")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Navigation Intelligente NAO")
    parser.add_argument("--ip", type=str, default="172.16.1.164",
                        help="Robot IP address")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--demo", action="store_true",
                        help="Mode démonstration")

    args = parser.parse_args()
    
    if args.demo or not QI_AVAILABLE:
        demo_navigation()
    else:
        # Mode robot réel
        session = qi.Session()
        try:
            session.connect("tcp://" + args.ip + ":" + str(args.port))
            print("✅ Connexion réussie au robot NAO!")
            
            nav_system = IntelligentNavigation(session)
            nav_system.start_intelligent_exploration()
            
            input("Appuyez sur Entrée pour arrêter...")
            nav_system.stop_intelligent_exploration()
            
        except RuntimeError as e:
            print(f"❌ Impossible de se connecter: {e}")
            print("🎮 Passage en mode DÉMO...")
            demo_navigation()