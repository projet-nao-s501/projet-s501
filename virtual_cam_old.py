#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

# Virtual Camera NAO - Version universelle avec mode démo
# Compatible Linux (v4l2loopback) et Windows (OpenCV)

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

# Needed packages to instantiate the virtual cam
# sudo apt install v4l2loopback-dkms v4l2loopback-utils 
# pip install qi argparse pyvirtualcam numpy==1.23.5 opencv-python==4.9.0.80

# Linux commands to reload the module
# sudo rmmod v4l2loopback
# sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="NAOcam" exclusive_caps=1

class MockVideoService:
    """Service vidéo simulé pour les tests"""
    def __init__(self):
        self.subscribed = False
        self.frame_count = 0
    
    def subscribeCamera(self, name_id, camera_index, resolution, color_space, fps):
        self.subscribed = True
        print(f"[DEMO] Abonnement caméra simulée (index: {camera_index}, résolution: {resolution})")
        return "_demo_cam"
    
    def getImageRemote(self, name_id):
        if not self.subscribed:
            return None
            
        # Génération d'une image de test colorée
        self.frame_count += 1
        width, height = 640, 480
        
        # Création d'une image de test avec un motif qui change
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient de couleur qui change avec le temps
        for y in range(height):
            for x in range(width):
                r = int((x + self.frame_count) % 255)
                g = int((y + self.frame_count // 2) % 255)
                b = int((x + y + self.frame_count // 4) % 255)
                img[y, x] = [r, g, b]
        
        # Ajout de texte
        cv2.putText(img, f"NAO Camera DEMO - Frame {self.frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        cv2.putText(img, f"IP: 172.16.1.164 (simulee)", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (255, 255, 255), 2)
        
        time.sleep(1/15)  # Simuler 15 FPS
        
        # Format compatible avec le code NAO
        return (width, height, 3, 0, 0, 0, img.tobytes())
    
    def unsubscribe(self, name_id):
        self.subscribed = False
        print(f"[DEMO] Désabonnement caméra: {name_id}")

class MockSession:
    """Session simulée pour les tests"""
    def service(self, service_name):
        if service_name == "ALVideoDevice":
            return MockVideoService()
        return None

def main(session):
    """Fonction principale de diffusion de la caméra NAO"""
    
    if QI_AVAILABLE:
        video_service = session.service("ALVideoDevice")
        print("🔗 Connexion au service vidéo NAO...")
    else:
        print("🎮 Mode DEMO - Simulation de caméra NAO")
        video_service = MockVideoService()
    
    # Paramètres de la caméra
    resolution = 2  # VGA (640x480)
    color_space = 11  # RGB
    fps = 15
    camera_index = 1  # Utiliser 0 ou 1 selon la caméra qui fonctionne
    
    print(f"📷 Configuration caméra:")
    print(f"   - Résolution: VGA (640x480)")
    print(f"   - Espace couleur: RGB")
    print(f"   - FPS: {fps}")
    print(f"   - Index caméra: {camera_index}")
    
    # Abonnement à la caméra
    name_id = ""
    name_id = video_service.subscribeCamera(name_id, camera_index, resolution, color_space, fps)
    print(f"✅ Abonné à la caméra: {name_id}")
    
    # Statistiques
    frame_count = 0
    start_time = time.time()
    
    print("\n🎦 DÉMARRAGE DU FLUX VIDÉO")
    print("=" * 50)
    
    if PYVIRTUALCAM_AVAILABLE:
        print("📺 Mode: Caméra virtuelle (v4l2loopback)")
        print("📺 Appareil: /dev/video10 (ou similar)")
        print("⌨️  Appuyez sur Ctrl+C pour quitter")
    else:
        print("📺 Mode: Fenêtre OpenCV")
        print("⌨️  Appuyez sur 'q' pour quitter")
        print("⌨️  Appuyez sur 's' pour prendre une capture")
    
    print("=" * 50)
    
    try:
        if PYVIRTUALCAM_AVAILABLE:
            # Mode caméra virtuelle avec v4l2loopback
            with pyvirtualcam.Camera(width=640, height=480, fps=20) as cam:
                while True:
                    image = video_service.getImageRemote(name_id)
                    if image is None:
                        print("⚠️ Pas d'image reçue")
                        continue

                    width, height = image[0], image[1]
                    array = image[6]
                    
                    if QI_AVAILABLE:
                        # Format NAO réel
                        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
                    else:
                        # Format démo
                        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

                    frame_count += 1
                    cam.send(img)
                    cam.sleep_until_next_frame()
        else:
            # Mode affichage OpenCV
            while True:
                image = video_service.getImageRemote(name_id)
                if image is None:
                    print("⚠️ Pas d'image reçue")
                    time.sleep(0.1)
                    continue
                
                # Extraction des données image
                width, height = image[0], image[1]
                array = image[6]
                
                if QI_AVAILABLE:
                    # Format NAO réel
                    img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
                else:
                    # Format démo
                    img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
                
                # Conversion RGB vers BGR pour OpenCV
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # Ajout d'informations sur l'image
                frame_count += 1
                current_time = time.time()
                
                # Overlay d'informations
                info_text = f"Frame: {frame_count} | Res: {width}x{height}"
                cv2.putText(img_bgr, info_text, 
                           (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 255, 0), 2)
                
                if QI_AVAILABLE:
                    status_text = f"NAO Camera - LIVE"
                    cv2.putText(img_bgr, status_text, 
                               (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (0, 255, 0), 2)
                else:
                    status_text = f"NAO Camera - DEMO MODE"
                    cv2.putText(img_bgr, status_text, 
                               (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (0, 255, 255), 2)
                
                # Affichage de l'image
                cv2.imshow("NAO Virtual Camera", img_bgr)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Arrêt demandé par l'utilisateur")
                    break
                elif key == ord('s'):
                    # Sauvegarde d'une capture
                    filename = f"nao_capture_{int(time.time())}.jpg"
                    cv2.imwrite(filename, img_bgr)
                    print(f"📸 Capture sauvée: {filename}")
                    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé (Ctrl+C)")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        print("\n🔧 Libération des ressources...")
        try:
            video_service.unsubscribe(name_id)
            print("✅ Désabonnement réussi")
        except Exception as e:
            print(f"⚠️ Erreur lors du désabonnement: {e}")
        
        if not PYVIRTUALCAM_AVAILABLE:
            cv2.destroyAllWindows()
        
        # Statistiques finales
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        print(f"\n📊 STATISTIQUES:")
        print(f"   - Frames total: {frame_count}")
        print(f"   - Durée: {total_time:.1f}s")
        print(f"   - FPS moyen: {avg_fps:.1f}")
        print("🏁 Fin du flux vidéo")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
