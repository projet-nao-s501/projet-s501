"""
Module permettant d'obtenir les événements du robot et les méthodes d'un service donnée
"""

from typing import Any


def GetEvenements(session : Any) -> None :
    """
Liste tous les événements existant dans le robot

Args:
    session: La session en cours avec le robot
    """
    memoire = session.service("ALMemory")
    for i in memoire.getEventList() :
        print(f"{i} \n")

def GetAllMethodes(session : Any, nomService : str) -> None :
    """
Listes toutes les méthodes existantes pour le service nomService

Args:
    session: La session en cours avec le robot
    nomService: le nom du service dont on veut les méthodes
    """
    service = session.service(nomService)
    meta = service.metaObject()
    
    for methode in meta.methods() :
        print(f"""
        ---
        
        Nom : {methode.name()}
        Arguments : {[arg.name() for arg in methode.parameters()]}
        Retour : {methode.returnSignature()}
        
        ---
              """)
if __name__ == '__main__' : pass