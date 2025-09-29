#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Virtual Camera NAO - Version ultra-simple
# Résout le problème des pixels manquants

import argparse
import sys
import time
import cv2
import numpy as np

# Import conditionnel pour mode démo
try:
    import qi
    QI_AVAILABLE = True
except ImportError:
    QI_AVAILABLE = False
    print("⚠️ Module 'qi' non disponible - Mode démo activé")

# Import conditionnel pour caméra virtuelle
try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False
    print("⚠️ pyvirtualcam non disponible - Affichage OpenCV uniquement")

class SimpleVideoService:
    """Service vidéo simple - génère des images complètes"""
    def __init__(self):
        self.subscribed = False
        self.frame_count = 0
        self.webcam = None
        
        # Essayer la webcam d'abord
        try:
            self.webcam = cv2.VideoCapture(0)
            if self.webcam.isOpened():
                print("📹 Webcam détectée - Utilisation du flux réel")
                self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            else:
                self.webcam = None
        except:
            self.webcam = None
    
    def subscribeCamera(self, name_id, camera_index, resolution, color_space, fps):
        self.subscribed = True
        if self.webcam:
            print("✅ Abonnement caméra réelle (webcam)")
        else:
            print("✅ Abonnement caméra simulée")
        return "simple_cam"
    
    def getImageRemote(self, name_id):
        if not self.subscribed:
            return None
            
        self.frame_count += 1
        
        # Utiliser webcam si disponible
        if self.webcam:
            ret, frame = self.webcam.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                # Convertir BGR vers RGB
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Overlay simple
                cv2.putText(img, f"NAO Simulation - Frame {self.frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, "Real Camera Feed", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                return (640, 480, 3, 0, 0, 0, img.tobytes())
        
        # Sinon, génération d'image simple et rapide
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Fond dégradé simple
        for y in range(480):
            color_intensity = int(100 + (y / 480) * 155)
            img[y, :] = [color_intensity, 50, 200 - color_intensity]
        
        # Formes géométriques simples
        cv2.circle(img, (160, 240), 50, (255, 100, 100), -1)
        cv2.circle(img, (320, 240), 40, (100, 255, 100), -1)
        cv2.circle(img, (480, 240), 35, (100, 100, 255), -1)
        
        # Rectangle animé
        x = int(50 + 50 * np.sin(self.frame_count * 0.1))
        cv2.rectangle(img, (x, 100), (x+100, 150), (255, 255, 100), -1)
        
        # Texte d'information
        cv2.putText(img, f"NAO Camera Demo - Frame #{self.frame_count}", 
                   (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(img, "IP: 172.16.1.164 (Simulation)", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 255), 1)
        
        cv2.putText(img, "Resolution: 640x480", 
                   (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        time.sleep(1/15)  # 15 FPS
        
        return (640, 480, 3, 0, 0, 0, img.tobytes())
    
    def unsubscribe(self, name_id):
        self.subscribed = False
        if self.webcam:
            self.webcam.release()
            print("📹 Webcam libérée")
        print("✅ Désabonnement caméra réussi")

class SimpleSession:
    def service(self, service_name):
        if service_name == "ALVideoDevice":
            return SimpleVideoService()
        return None

def main(session):
    """Fonction principale ultra-simple"""
    
    # Déterminer le type de session
    if hasattr(session, 'service'):
        try:
            video_service = session.service("ALVideoDevice")
            print("🔗 Service vidéo NAO connecté")
        except:
            print("🎮 Mode simulation simple")
            video_service = SimpleVideoService()
    else:
        print("🎮 Mode simulation simple")
        video_service = SimpleVideoService()
    
    # Configuration simple
    name_id = video_service.subscribeCamera("", 1, 2, 11, 15)
    
    print("\n📺 DÉMARRAGE - Appuyez sur 'q' pour quitter")
    print("=" * 50)
    
    frame_count = 0
    
    try:
        while True:
            image = video_service.getImageRemote(name_id)
            if image is None:
                time.sleep(0.1)
                continue
            
            width, height = image[0], image[1]
            array = image[6]
            
            # Conversion directe
            img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Affichage
            cv2.imshow("NAO Simple Camera", img_bgr)
            
            # Contrôle
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, img_bgr)
                print(f"💾 Capture sauvée: {filename}")
            
            frame_count += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    finally:
        video_service.unsubscribe(name_id)
        cv2.destroyAllWindows()
        print(f"🏁 Arrêt - {frame_count} frames affichées")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.16.1.164")
    parser.add_argument("--port", type=int, default=9559)
    
    args = parser.parse_args()
    
    print("📷 NAO SIMPLE CAMERA")
    print(f"🔗 IP: {args.ip}:{args.port}")
    
    if QI_AVAILABLE:
        session = qi.Session()
        try:
            session.connect(f"tcp://{args.ip}:{args.port}")
            print("✅ Connexion robot réussie")
            main(session)
        except:
            print("⚠️ Robot indisponible - Mode simulation")
            main(SimpleSession())
    else:
        main(SimpleSession())