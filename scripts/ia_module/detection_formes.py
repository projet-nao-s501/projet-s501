import cv2
import os
import requests
from ultralytics import YOLO

MODEL_FILENAME = "deepfashion2_yolov8s-seg.pt"

def lancer_segmentation():
    model = YOLO(MODEL_FILENAME)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret: break

        results = model.predict(source=frame, conf=0.4, stream=True, verbose=False)

        for r in results:
            annotated_frame = r.plot()

            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                print(f"NAO voit précisément : {label}")

        cv2.imshow("IA Segmentation Fashion", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    lancer_segmentation()