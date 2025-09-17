# Projet nao-s501

## Installation

### Docker

```bash
docker build -t s501-nao .
docker run -it --name nao-s501 -p 60323:60323 s501-nao bash
```

### OS Linux

- Installer les paquages suivants :
  - build-essential
  - cmake
  - libpython3-dev
  - python3-venv

- cloner le projet :

```bash
git clone https://github.com/zykogithub/s501-nao.git
```

- Créer un fichier requirements.txt avec comme librairies à installer :
  - qi
- remarques : de futurs librairies pourraient être utilisé à l'avenir

- Créer l'environnement virtuel

```bash
python3 -m venv venv
/app/venv/bin/pip install --upgrade pip
/app/venv/bin/pip install -r requirements.txt
```

## Démarrez le script

### Lancement Docker

Quelques commandes supplémentaires sont à exécutez en fonction de votre OS, si vous utilisez le simulateur de naoqi

#### Windows

- Allez dans :

> C:\Program Files (x86)\Aldebaran Robotics\Choregraphe Suite 2.1\bin

- executez la commande :

```powershell
naoqi-bin.exe --broker-ip 0.0.0.0 --broker-port 60323
# permet au simulateur de recevoir des connexions depuis l'extérieur
```

- Remarque : n'ayez pas chorégraphe de lancer

#### Linux/MacOs

- sur docker vous devez ajoutez une option dans le docker run :

```bash
docker run -it --network host projet-nao s501-nao
# connecte le conteneur au réseau de l'hôte
```

- Remarque : vous pouvez aussi créer un bridge avec **docker network create <nom_bridge>** puis connecter le conteneur à ce bridge via l'option **--network <nom_bridge>**

### Lancer le projet

- Démarez l'environnement virtuel python

```bash
source venv/bin/activate
```

- Aller dans le dossier

> projet_s501/app/scripts

- Executez le fichier test

```bash
python main.py --ip <adresse IP> --port <numéro de port>
```

## Organisation du git

Tout est donné dans ce [lien](https://naos501g1.atlassian.net/wiki/spaces/SCRUM/pages/3244054/R+gle+de+d+veloppement?atlOrigin=eyJpIjoiM2RjZTEyNTI4YmY2NDQzY2I3OWU2ODU5YTdmMWJjODMiLCJwIjoiaiJ9)

