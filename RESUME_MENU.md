# 📋 RÉSUMÉ DU MENU SIMPLE NAO

## 🎯 QU'EST-CE QUE LE MENU SIMPLE ?

Le **menu simple** (`nao_menu_simple.py`) est un **système de contrôle interactif** pour le robot NAO v6 qui permet de :

- Contrôler le robot via un menu texte simple
- Exécuter des actions prédéfinies (postures, scans, caméra, alertes)
- Gérer les mouvements de la tête, des bras et du corps du robot
- Utiliser la caméra du robot en temps réel

---

## 🔧 FONCTIONS DISPONIBLES DANS LE MENU

### **1. Debout** (`stand_up`)
- **Fonction** : Met le robot en position debout
- **Actions** :
  - Réveille le robot (`motion.wakeUp()`)
  - Met le robot en posture "StandInit"
- **Utilisation** : Démarre toujours par cette option avant les autres mouvements

### **2. S'asseoir** (`sit_down`)
- **Fonction** : Met le robot en position assise
- **Actions** :
  - Met le robot en posture "Sit"
- **Utilisation** : Économise la batterie, position de repos

### **3. Flux caméra NAO + Caméra virtuelle** (`show_camera_stream`)
- **Fonction** : Affiche le flux vidéo de la caméra du robot NAO
- **Actions** :
  - Se connecte à la caméra bottom (index 1) du robot
  - Affiche le flux en temps réel (640x480, 15 FPS)
  - Crée une caméra virtuelle utilisable dans Zoom/Teams (si pyvirtualcam installé)
- **Navigation** : Appuyer sur 'q' pour quitter
- **Dépendances** : Requiert OpenCV (`cv2`) et optionnellement `pyvirtualcam`

### **4. Scan vertical 4 crans** (`scan_vertical_4_crans`)
- **Fonction** : Effectue un scan vertical du bas vers le haut avec 4 positions
- **Actions** :
  - Mouvement de la tête uniquement
  - 4 positions : Genoux → Torse → Poitrine → Tête
  - 4 secondes d'attente à chaque position
  - Retour au centre à la fin
- **Utilisation** : Scan rapide vertical pour observer une zone

### **5. Scan vertical avec bras** (`scan_vertical_avec_bras`)
- **Fonction** : Scan vertical AVANCÉ qui permet de regarder très haut (même le plafond)
- **Actions** :
  - **Phase 1** : Prépare le robot
    - Met les bras très en avant (contrepoids)
    - Pencher le corps en arrière (HipPitch)
    - Surveillance de l'équilibre avec capteurs gyroscopiques
  - **Phase 2** : Scan vertical
    - 4 positions : Genoux → Torse → Poitrine → Haut sécurisé
    - Surveillance continue de l'équilibre
  - **Phase 3** : Retour à la normale
    - Tête au centre
    - Corps droit
    - Bras le long du corps
- **Sécurité** : 
  - Vérifie l'équilibre avant/après chaque mouvement
  - Mouvements très lents pour éviter la chute
  - Système de récupération d'urgence si problème
- **Utilisation** : Scan complet pour voir très haut (plafond, haut des murs)

### **6. Scan tête complet** (`scan_tete_complet`)
- **Fonction** : Effectue un balayage complet de la tête (horizontal puis vertical)
- **Actions** :
  - **Horizontal** : Gauche max → Droite max → Centre
  - **Vertical** : Bas max → Haut max → Centre
- **Utilisation** : Balayage complet pour observer une pièce entière

### **7. Pointer vers personne + Alerte** (`point_and_alert`)
- **Fonction** : Le robot pointe vers une personne debout et dit "Intrus trouvé"
- **Actions** :
  - Lève le bras droit à 75° vers le haut
  - Pointe vers une personne debout (hauteur de tête)
  - Utilise le service de synthèse vocale (`ALTextToSpeech`)
  - Dit "Intrus trouvé!"
  - Remet le bras en position normale
- **Utilisation** : Détection d'intrusion avec alerte vocale et gestuelle

### **8. Reset position** (`reset_position`)
- **Fonction** : Remet le robot en position neutre
- **Actions** :
  - Tête au centre (Yaw=0, Pitch=0)
  - Bras en position neutre
  - Mains ouvertes
- **Utilisation** : Réinitialisation après des mouvements complexes

### **9. Quitter**
- **Fonction** : Ferme le programme proprement
- **Actions** :
  - Met le robot au repos (`motion.rest()`)
  - Ferme la connexion

---

## 📂 FICHIERS NÉCESSAIRES

### **Fichiers requis** :
- ✅ `nao_menu_simple.py` - Script principal
- ✅ `config.json` - Configuration (IP du robot)

### **Fichiers optionnels** (documentation) :
- `README_MENU_SIMPLE.md` - Guide d'installation
- `OPTION_5_TECHNIQUE.md` - Détails techniques option 5
- `COMPARAISON_SCANS.md` - Comparaison des scans

### **Fichiers supprimés** (inutiles) :
- ❌ `test_*.py` - Fichiers de test
- ❌ `virtual_cam.py` - Fonctionnalité intégrée dans l'option 3

---

## 🔗 SERVICES NAO UTILISÉS

Le menu utilise les services NAOqi suivants :

1. **ALMotion** - Contrôle des mouvements du robot
2. **ALRobotPosture** - Postures prédéfinies (debout, assis)
3. **ALVideoDevice** - Accès à la caméra du robot
4. **ALMemory** - Accès aux capteurs (gyroscope pour équilibre)
5. **ALTextToSpeech** - Synthèse vocale (option 7)

---

## ⚙️ FONCTIONNEMENT TECHNIQUE

### **Structure du code** :

1. **Connexion** : Charge `config.json` → Connexion au robot via IP
2. **Menu principal** : Boucle infinie qui affiche le menu et attend le choix
3. **Exécution** : Appelle la fonction correspondante au choix
4. **Retour au menu** : Après chaque action, retour au menu (sauf option 9)

### **Sécurité** :
- Vérification de l'équilibre avec capteurs gyroscopiques (option 5)
- Gestion d'erreurs avec try/except
- Récupération d'urgence en cas de problème d'équilibre
- Arrêt propre du robot à la fin

---

## 🎓 UTILISATION TYPIQUE

**Exemple de session** :
```
1. Lancer : python nao_menu_simple.py
2. Option 1 : Debout (mettre le robot debout)
3. Option 6 : Scan tête complet (observer la pièce)
4. Option 5 : Scan avec bras (regarder très haut)
5. Option 7 : Pointer + Alerte (si intrusion détectée)
6. Option 8 : Reset (remettre en position neutre)
7. Option 2 : S'asseoir (économiser batterie)
8. Option 9 : Quitter
```

---

## ✅ AMÉLIORATIONS RÉCENTES

- ❌ **Mode démo supprimé** : Le script nécessite maintenant une vraie connexion au robot
- ❌ **Fichiers de test supprimés** : Nettoyage des fichiers inutiles
- ✅ **Code simplifié** : Plus de conditions de démo, code plus clair
- ✅ **Meilleure gestion d'erreurs** : Arrêt immédiat si connexion impossible

