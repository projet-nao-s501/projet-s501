import os
from ultralytics import YOLO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = os.path.join(SCRIPT_DIR, "deepfashion2_yolov8s-seg.pt")

def detection_formes(frame):
    model = YOLO(MODEL_FILENAME)

    results = model.predict(source=frame, conf=0.4, stream=True, verbose=False)

    for r in results:
        annotated_frame = r.plot()

        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            print(f"NAO voit précisément : {label}")

    return annotated_frame
