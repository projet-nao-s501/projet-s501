<<<<<<< HEAD
# 🤖 NAO Menu Simple - Guide d'Installation et d'Utilisation

## 📋 RÉSUMÉ DU PROJET

Ce projet contient un script Python (`nao_menu_simple.py`) pour contrôler un robot NAO v6 avec un menu interactif.

### 🎯 Fonctionnalités disponibles :

1. **Debout** - Met le robot en position debout
2. **S'asseoir** - Met le robot en position assise
3. **📹 Flux caméra direct** - Affiche le flux de la caméra frontale (appuyez sur 'q' pour quitter)
4. **Scan vertical 4 crans** - Scan du haut vers le bas (4 secondes par cran)
5. **🔥 Scan EXTRÊME avec bassin** - Utilise bras + bassin pour regarder très haut (même le plafond !)
6. **Scan tête complet** - Mouvements gauche/droite puis haut/bas
7. **Pointer + alerte** - Pointe vers le haut et dit "Intrus trouvé"
8. **Reset position** - Remet la tête et les bras en position neutre
9. **Quitter** - Quitte le programme

---

## 📦 INSTALLATION DES DÉPENDANCES

### 1. Installer les packages Python nécessaires :

```powershell
# SDK NAO (obligatoire pour se connecter au robot)
pip install qi

# OpenCV (obligatoire pour la fonction caméra)
pip install opencv-python

# NumPy (obligatoire pour le traitement d'image)
pip install numpy
```

### 2. Vérifier l'installation :

```powershell
python -c "import qi; import cv2; import numpy; print('✓ Tous les packages sont installés !')"
```

---

## ⚙️ CONFIGURATION

### Fichier `config.json` :

Le fichier `config.json` contient l'adresse IP du robot NAO :

```json
{
    "robot_ip": "172.16.1.163",
    "robot_port": 9559
}
```

**Pour changer l'IP du robot :**
1. Ouvrez `config.json` dans un éditeur de texte
2. Modifiez la valeur de `"robot_ip"`
3. Sauvegardez le fichier

---

## 🚀 LANCEMENT DU SCRIPT

### Depuis PowerShell :

```powershell
# Aller dans le dossier du projet
cd C:\Nao\projet-s501

# Lancer le script
python nao_menu_simple.py
```

### Depuis VS Code :

1. Ouvrez le fichier `nao_menu_simple.py`
2. Appuyez sur **F5** pour lancer
3. Ou clic droit → "Run Python File in Terminal"

---

## 🎮 UTILISATION

### Au lancement :

1. Le script vous demande si vous voulez utiliser le **mode DÉMO** (sans robot) :
   - Tapez **`n`** pour utiliser le vrai robot
   - Tapez **`o`** pour tester sans robot (simulation)

2. Le script se connecte au robot (si mode réel)

3. Le menu principal s'affiche

### Navigation dans le menu :

- Tapez le **numéro de l'option** (1 à 9)
- Appuyez sur **Entrée**
- L'action s'exécute
- Le menu se réaffiche automatiquement

### Quitter :

- Tapez **`9`** et appuyez sur Entrée
- Ou appuyez sur **Ctrl+C** pour interrompre

---

## 🔥 FONCTIONNALITÉS AVANCÉES

### Option 3 : Flux caméra direct

Cette fonction affiche le flux de la caméra frontale du robot en temps réel :

- Utilise `ALVideoDevice.subscribeCamera()`
- Résolution : 640x480 (VGA)
- FPS : 30
- Appuyez sur **'q'** dans la fenêtre vidéo pour quitter

### Option 5 : Scan EXTRÊME avec bassin

Cette fonction est la plus impressionnante ! Le robot :

1. **Phase 1** : Prépare son corps
   - Met les bras vers l'avant
   - Incline le bassin vers l'arrière

2. **Phase 2** : Scan du haut vers le bas
   - Regarde presque à la verticale (plafond)
   - Descend progressivement jusqu'aux genoux
   - 4 secondes par position

3. **Phase 3** : Retour à la normale
   - Bassin en position droite
   - Bras le long du corps
   - Tête au centre

Grâce à l'utilisation du bassin (HipPitch), le robot peut regarder **beaucoup plus haut** qu'avec la tête seule !

---

## 🐛 DÉPANNAGE

### Erreur : "Module 'qi' not found"
```powershell
pip install qi
```

### Erreur : "Module 'cv2' not found"
```powershell
pip install opencv-python
```

### Erreur : "Module 'numpy' not found"
```powershell
pip install numpy
```

### Erreur : "Impossible de se connecter au robot"

1. Vérifiez que le robot est allumé
2. Vérifiez l'IP dans `config.json`
3. Vérifiez que votre ordinateur est sur le même réseau
4. Testez la connexion :
   ```powershell
   ping 172.16.1.163
   ```

### La caméra ne s'affiche pas (Option 3)

1. Vérifiez qu'OpenCV est installé : `pip list | findstr opencv`
2. Vérifiez que le robot est connecté
3. Essayez de fermer d'autres programmes utilisant la caméra

### Le robot perd l'équilibre pendant le scan extrême (Option 5)

1. Assurez-vous que le robot est sur une surface plane
2. Vérifiez que les batteries sont suffisamment chargées
3. Le robot doit être en position **debout** avant de lancer le scan

---

## 📁 STRUCTURE DES FICHIERS

```
C:\Nao\projet-s501\
│
├── nao_menu_simple.py          # Script principal avec menu
├── config.json                  # Configuration (IP du robot)
├── README_MENU_SIMPLE.md        # Ce fichier (instructions)
│
├── virtual_cam_simple.py        # Script caméra virtuelle (optionnel)
├── nao_menu_complet.py          # Version complète avec plus de fonctions
└── ... (autres fichiers)
```

---

## 📝 NOTES IMPORTANTES

### Sécurité :

- Le robot doit avoir de l'espace autour de lui pour bouger
- Ne pas lancer le scan extrême si le robot est près d'un bord/escalier
- Toujours superviser le robot pendant l'exécution

### Performance :

- Le scan avec bassin (Option 5) utilise beaucoup de moteurs
- Les batteries se déchargent plus vite
- Laisser le robot se reposer entre les scans

### Mode DÉMO :

- Utile pour tester le script sans robot
- Affiche des messages simulant les actions
- Ne nécessite pas le SDK NAO (module `qi`)

---

## 💡 EXEMPLES D'UTILISATION

### Exemple 1 : Scan rapide d'une pièce

1. Lancer le script : `python nao_menu_simple.py`
2. Choisir **mode réel** (n)
3. Option **1** : Debout
4. Option **6** : Scan tête complet (balayage horizontal et vertical)
5. Option **8** : Reset position
6. Option **9** : Quitter

### Exemple 2 : Scan vertical approfondi

1. Lancer le script
2. Choisir **mode réel**
3. Option **1** : Debout
4. Option **5** : Scan EXTRÊME avec bassin (pour voir très haut)
5. Option **8** : Reset position
6. Option **2** : S'asseoir (économiser la batterie)
7. Option **9** : Quitter

### Exemple 3 : Test de la caméra

1. Lancer le script
2. Choisir **mode réel**
3. Option **1** : Debout
4. Option **3** : Flux caméra direct
5. Observer le flux vidéo
6. Appuyer sur **'q'** dans la fenêtre pour quitter
7. Option **9** : Quitter le menu

---

## 🎓 PROJET S501 - IUT

Ce script a été développé dans le cadre du **Projet S501** pour le contrôle d'un robot NAO v6.

### Objectifs atteints :

✅ Connexion et contrôle du robot NAO  
✅ Changements de posture (debout/assis)  
✅ Accès au flux vidéo de la caméra frontale  
✅ Scans verticaux et horizontaux avec la tête  
✅ Utilisation du bassin pour étendre la plage de vision  
✅ Compensation d'équilibre avec les bras  
✅ Interface utilisateur simple et intuitive  

---

## 📧 CONTACT

Pour toute question sur ce projet, contactez votre enseignant ou référez-vous à la documentation officielle NAOqi.

**Documentation NAOqi :** http://doc.aldebaran.com/2-8/index.html

---

**Bon contrôle de votre robot NAO ! 🤖✨**
=======
# 🤖 NAO Menu Simple - Guide d'Installation et d'Utilisation

## 📋 RÉSUMÉ DU PROJET

Ce projet contient un script Python (`nao_menu_simple.py`) pour contrôler un robot NAO v6 avec un menu interactif.

### 🎯 Fonctionnalités disponibles :

1. **Debout** - Met le robot en position debout
2. **S'asseoir** - Met le robot en position assise
3. **📹 Flux caméra direct** - Affiche le flux de la caméra frontale (appuyez sur 'q' pour quitter)
4. **Scan vertical 4 crans** - Scan du haut vers le bas (4 secondes par cran)
5. **🔥 Scan EXTRÊME avec bassin** - Utilise bras + bassin pour regarder très haut (même le plafond !)
6. **Scan tête complet** - Mouvements gauche/droite puis haut/bas
7. **Pointer + alerte** - Pointe vers le haut et dit "Intrus trouvé"
8. **Reset position** - Remet la tête et les bras en position neutre
9. **Quitter** - Quitte le programme

---

## 📦 INSTALLATION DES DÉPENDANCES

### 1. Installer les packages Python nécessaires :

```powershell
# SDK NAO (obligatoire pour se connecter au robot)
pip install qi

# OpenCV (obligatoire pour la fonction caméra)
pip install opencv-python

# NumPy (obligatoire pour le traitement d'image)
pip install numpy
```

### 2. Vérifier l'installation :

```powershell
python -c "import qi; import cv2; import numpy; print('✓ Tous les packages sont installés !')"
```

---

## ⚙️ CONFIGURATION

### Fichier `config.json` :

Le fichier `config.json` contient l'adresse IP du robot NAO :

```json
{
    "robot_ip": "172.16.1.163",
    "robot_port": 9559
}
```

**Pour changer l'IP du robot :**
1. Ouvrez `config.json` dans un éditeur de texte
2. Modifiez la valeur de `"robot_ip"`
3. Sauvegardez le fichier

---

## 🚀 LANCEMENT DU SCRIPT

### Depuis PowerShell :

```powershell
# Aller dans le dossier du projet
cd C:\Nao\projet-s501

# Lancer le script
python nao_menu_simple.py
```

### Depuis VS Code :

1. Ouvrez le fichier `nao_menu_simple.py`
2. Appuyez sur **F5** pour lancer
3. Ou clic droit → "Run Python File in Terminal"

---

## 🎮 UTILISATION

### Au lancement :

1. Le script vous demande si vous voulez utiliser le **mode DÉMO** (sans robot) :
   - Tapez **`n`** pour utiliser le vrai robot
   - Tapez **`o`** pour tester sans robot (simulation)

2. Le script se connecte au robot (si mode réel)

3. Le menu principal s'affiche

### Navigation dans le menu :

- Tapez le **numéro de l'option** (1 à 9)
- Appuyez sur **Entrée**
- L'action s'exécute
- Le menu se réaffiche automatiquement

### Quitter :

- Tapez **`9`** et appuyez sur Entrée
- Ou appuyez sur **Ctrl+C** pour interrompre

---

## 🔥 FONCTIONNALITÉS AVANCÉES

### Option 3 : Flux caméra direct

Cette fonction affiche le flux de la caméra frontale du robot en temps réel :

- Utilise `ALVideoDevice.subscribeCamera()`
- Résolution : 640x480 (VGA)
- FPS : 30
- Appuyez sur **'q'** dans la fenêtre vidéo pour quitter

### Option 5 : Scan EXTRÊME avec bassin

Cette fonction est la plus impressionnante ! Le robot :

1. **Phase 1** : Prépare son corps
   - Met les bras vers l'avant
   - Incline le bassin vers l'arrière

2. **Phase 2** : Scan du haut vers le bas
   - Regarde presque à la verticale (plafond)
   - Descend progressivement jusqu'aux genoux
   - 4 secondes par position

3. **Phase 3** : Retour à la normale
   - Bassin en position droite
   - Bras le long du corps
   - Tête au centre

Grâce à l'utilisation du bassin (HipPitch), le robot peut regarder **beaucoup plus haut** qu'avec la tête seule !

---

## 🐛 DÉPANNAGE

### Erreur : "Module 'qi' not found"
```powershell
pip install qi
```

### Erreur : "Module 'cv2' not found"
```powershell
pip install opencv-python
```

### Erreur : "Module 'numpy' not found"
```powershell
pip install numpy
```

### Erreur : "Impossible de se connecter au robot"

1. Vérifiez que le robot est allumé
2. Vérifiez l'IP dans `config.json`
3. Vérifiez que votre ordinateur est sur le même réseau
4. Testez la connexion :
   ```powershell
   ping 172.16.1.163
   ```

### La caméra ne s'affiche pas (Option 3)

1. Vérifiez qu'OpenCV est installé : `pip list | findstr opencv`
2. Vérifiez que le robot est connecté
3. Essayez de fermer d'autres programmes utilisant la caméra

### Le robot perd l'équilibre pendant le scan extrême (Option 5)

1. Assurez-vous que le robot est sur une surface plane
2. Vérifiez que les batteries sont suffisamment chargées
3. Le robot doit être en position **debout** avant de lancer le scan

---

## 📁 STRUCTURE DES FICHIERS

```
C:\Nao\projet-s501\
│
├── nao_menu_simple.py          # Script principal avec menu
├── config.json                  # Configuration (IP du robot)
├── README_MENU_SIMPLE.md        # Ce fichier (instructions)
│
├── virtual_cam_simple.py        # Script caméra virtuelle (optionnel)
├── nao_menu_complet.py          # Version complète avec plus de fonctions
└── ... (autres fichiers)
```

---

## 📝 NOTES IMPORTANTES

### Sécurité :

- Le robot doit avoir de l'espace autour de lui pour bouger
- Ne pas lancer le scan extrême si le robot est près d'un bord/escalier
- Toujours superviser le robot pendant l'exécution

### Performance :

- Le scan avec bassin (Option 5) utilise beaucoup de moteurs
- Les batteries se déchargent plus vite
- Laisser le robot se reposer entre les scans

### Mode DÉMO :

- Utile pour tester le script sans robot
- Affiche des messages simulant les actions
- Ne nécessite pas le SDK NAO (module `qi`)

---

## 💡 EXEMPLES D'UTILISATION

### Exemple 1 : Scan rapide d'une pièce

1. Lancer le script : `python nao_menu_simple.py`
2. Choisir **mode réel** (n)
3. Option **1** : Debout
4. Option **6** : Scan tête complet (balayage horizontal et vertical)
5. Option **8** : Reset position
6. Option **9** : Quitter

### Exemple 2 : Scan vertical approfondi

1. Lancer le script
2. Choisir **mode réel**
3. Option **1** : Debout
4. Option **5** : Scan EXTRÊME avec bassin (pour voir très haut)
5. Option **8** : Reset position
6. Option **2** : S'asseoir (économiser la batterie)
7. Option **9** : Quitter

### Exemple 3 : Test de la caméra

1. Lancer le script
2. Choisir **mode réel**
3. Option **1** : Debout
4. Option **3** : Flux caméra direct
5. Observer le flux vidéo
6. Appuyer sur **'q'** dans la fenêtre pour quitter
7. Option **9** : Quitter le menu

---

## 🎓 PROJET S501 - IUT

Ce script a été développé dans le cadre du **Projet S501** pour le contrôle d'un robot NAO v6.

### Objectifs atteints :

✅ Connexion et contrôle du robot NAO  
✅ Changements de posture (debout/assis)  
✅ Accès au flux vidéo de la caméra frontale  
✅ Scans verticaux et horizontaux avec la tête  
✅ Utilisation du bassin pour étendre la plage de vision  
✅ Compensation d'équilibre avec les bras  
✅ Interface utilisateur simple et intuitive  

---

## 📧 CONTACT

Pour toute question sur ce projet, contactez votre enseignant ou référez-vous à la documentation officielle NAOqi.

**Documentation NAOqi :** http://doc.aldebaran.com/2-8/index.html

---

**Bon contrôle de votre robot NAO ! 🤖✨**
>>>>>>> 5e07dd438da7a7fa89421b80f169f1629dcf538c
