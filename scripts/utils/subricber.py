"""
Module permettant de s'abonner à un événement dans le robot
"""

from typing import Any, Callable

def Subriber(session : Any, onEvent : Callable[[Any], None], eventName : str) -> None:
    """
    S'abonne à l'événement eventName du robot
    
    Args:
        session: Session en cours avec le robot
        onEvent: fonction appelé si l'evenement se produit
        eventName: nom de l'evenment auquel la fonction s'abonne 
    """
    memoire = session.service("ALMemory")
    subriber = memoire.subscriber(eventName)
    subriber.signal.connect(onEvent) # connect ne reverra rien, il faudra se débrouiller autremen si vous voulez réutiliser la valariable ailleurs

if __name__ == '__main__' : pass