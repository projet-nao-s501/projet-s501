import cv2
import os
import time
import numpy as np
from ultralytics import YOLO
from detection_couleurs import detection_couleurs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = os.path.join(SCRIPT_DIR, "deepfashion2_yolov8s-seg.pt")
model = YOLO(MODEL_FILENAME)

def extraire_segment(frame, mask, box):

    mask_data = mask.data[0].cpu().numpy()
    mask_binary = cv2.resize(mask_data, (frame.shape[1], frame.shape[0]))
    mask_binary = (mask_binary > 0.5).astype(np.uint8) * 255

    isolated_object = cv2.bitwise_and(frame, frame, mask=mask_binary)

    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    crop_detoure = isolated_object[y1:y2, x1:x2]
    
    return crop_detoure

def detection_formes():
    cap = cv2.VideoCapture(0)
    
    dernier_temps_print = 0 

    while True:
        ret, frame = cap.read()
        if not ret: break

        results = model.predict(source=frame, conf=0.4, verbose=False)
        
        infos_a_afficher = []

        for r in results:
            annotated_frame = r.plot() 

            if r.masks is not None:
                for i, (mask, box) in enumerate(zip(r.masks, r.boxes)):
                    label = model.names[int(box.cls[0])]
                    obj_id = f"{label}_{i}"
                    
                    vêtement_seul = extraire_segment(frame, mask, box)

                    if vêtement_seul.size > 0:
                        couleur = detection_couleurs(vêtement_seul)
                        infos_a_afficher.append(f"{label}: {couleur}")

        temps_actuel = time.time()
        
        if temps_actuel - dernier_temps_print >= 1.0:
            if infos_a_afficher:
                print(f" | ".join(infos_a_afficher))
            
            dernier_temps_print = temps_actuel

        cv2.imshow("IA Segmentation Fashion", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detection_formes()
