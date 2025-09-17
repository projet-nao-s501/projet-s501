# Exemple de Projet NAO avec recuperation du flux video

## Installation de packages sur Linux
```bash
sudo apt update
sudo sudo apt install v4l2loopback-dkms v4l2loopback-utils 
````

## Mise en place coté Visuel Studio Code ou VSCodium
Installer l'extension Python


## Mise en place de l'environnement virtuel Python
Cloner ce dépôt puis mettre en place
un environnement virtuel Python. Ensuite installer 
les dépendances :
```bash
pip install qi argparse pyvirtualcam numpy==1.23.5 opencv-python==4.9.0.80
pip install tensorflow==2.12.1
```

## Lancement de la caméra virtuelle
Après avoir changé l'adresse IP du robot dans `.vscode/launch.json`
lancer le script `virtual_cam.py` en tapant sur __F5__

## Lancement du script principal
Après avoir changé l'adresse IP du robot dans `.vscode/launch.json`
lancer le script `main.py` en tapant sur __F5__
