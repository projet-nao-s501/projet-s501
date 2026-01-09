from ultralytics import YOLO
import cv2

# Charger le modèle YOLOv8 une seule fois
model = YOLO("model/best.pt")
# model = YOLO("yolov8m.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    # ici ret c'est pour retiourner un booléan qui va dire si la capture de l'image est bien 
    # ici frame est l'image capturer par la webcam
    ret, frame = cap.read()  # Récupère une image
    if not ret:
        print("Impossible de lire l'image depuis la webcam")
        break

    results = model(frame, conf=0.8)

    frame_box = results[0].plot()

    frame_box = cv2.resize(frame_box, (900, 900))

    cv2.imshow("Résultat détection YOLO", frame_box)
        
        
    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

