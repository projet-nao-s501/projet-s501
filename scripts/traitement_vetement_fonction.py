from ultralytics import YOLO
import cv2

# Charger le modèle YOLOv8 une seule fois (en dehors de la fonction)
model = YOLO("model/best.pt")

def visualiser_dataset(image_data):
    
    # Détection YOLO sur l'image
    results = model(image_data, conf=0.8)
    
    # Tracer les boîtes de détection
    frame_box = results[0].plot()
    
    # Redimensionner l'image
    frame_box = cv2.resize(frame_box, (900, 900))
    
    return frame_box
   
   

