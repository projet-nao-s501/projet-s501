import cv2
import os
import time
import numpy as np
from ultralytics import YOLO
from scripts.ia_module.detection_couleurs import detection_couleurs
from scripts.meca_module.reaction_nao import naoDab, naoDanse

sessionNao = None

vetements = {
	"pull": "long_sleeved_shirt",
	"tshirt": "short_sleeved_shirt",
	"veste-manche-courte": "short_sleeved_outwear",
	"veste-manche-longue": "long_sleeved_outwear",
	"gilet": "vest",
	"sacoche": "sling",
	"short": "shorts",
	"pantalon": "trousers",
	"jupe": "skirt",
	"robe-manche-courte": "short_sleeved_dress",
	"robe-manche-30longue": "long_sleeved_dress",
	"robe-tailleur": "vest_dress",
	"robe-bretelle": "sling_dress"
}


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

def detection_formes(frame,tab,session):
  
    tts = session.service("ALTextToSpeech")
    results = model.predict(source=frame, conf=0.4, verbose=False)

    infos_a_afficher = {}

    for r in results:
        annotated_frame = r.plot() 

        if r.masks is not None:
            for i, (mask, box) in enumerate(zip(r.masks, r.boxes)):
                label = model.names[int(box.cls[0])]

                vêtement_seul = extraire_segment(frame, mask, box)

                if vêtement_seul.size > 0:
                    couleur = detection_couleurs(vêtement_seul)
                    infos_a_afficher[label] = couleur
    
    print(infos_a_afficher)
    cv2.imshow("IA Segmentation Fashion", annotated_frame)

    # description du robot 
    desc_robo_haut = tab[0] 
    desc_robo_bas = tab[1]

    # description du modèle ( ce que voit l'ia)
    changer =  desc_robo_haut.split(" ")
    print("changer : ", changer)

    desc_haut_ia = changer[0]
    desc_couleur_haut_ia = changer[1]

    changer2 =   desc_robo_bas.split(" ")
    print("changer2 : ", changer2)

    desc_bas_ia = changer2[0]
    desc_couleur_bas_ia = changer2[1]

    #comparaison

    label_haut = vetements[desc_haut_ia]
    label_bas = vetements[desc_bas_ia]

    print("haut : ", label_haut, " bas : ", label_bas)


    #infos = ["long_sleeved_shirt":"rouge", "trousers":"black"]
    if (
    infos_a_afficher.get(label_haut) == desc_couleur_haut_ia
    and infos_a_afficher.get(label_bas) == desc_couleur_bas_ia):
        tts.say("J'ai trouvé !")
        naoDab(session)
        naoDanse(session)
        return 0
    
    
    tts.say("Ce n'est pas toi !")
    return 1
