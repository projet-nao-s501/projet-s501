from ultralytics import YOLO
import cv2



model_detect = YOLO("scripts/ia_module/best.pt")
model_classify = YOLO("scripts/ia_module/deepfashion2_yolov8s-seg.pt")

image = cv2.imread("scripts/utils/Friend_group.jpg")
image = cv2.resize(image, (900, 900)) 

def detection_and_classification(image):

    results = model_detect(image, conf=0.8)
    print("Détections best.pt :", len(results[0].boxes))

    frame = image.copy()

    for box in results[0].boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            continue

        results_cls = model_classify(crop, conf=0.4, verbose=False)

        if len(results_cls[0].boxes) > 0:
            cls_id = int(results_cls[0].boxes[0].cls[0])
            label = model_classify.names[cls_id]
        else:
            label = "Non reconnu"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        print("DeepFashion :", len(results_cls[0].boxes))

    return frame


result = detection_and_classification(image)

cv2.imshow("Resultat des fusions des models", result)
cv2.waitKey(0)
cv2.destroyAllWindows()




