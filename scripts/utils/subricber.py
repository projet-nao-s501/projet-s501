"""
Module permettant de s'abonner et se désaboonner à un événement dans le robot
"""

from typing import Any, Callable

def Subscriber(session : Any, onEvent : Callable[[Any], None], eventName : str) -> None:
    """
    S'abonne à l'événement `eventName` du robot
    
    Args:
        session: Session en cours avec le robot
        onEvent: fonction appelé
        si l'evenement se produit
        eventName: nom de l'evenment auquel la fonction s'abonne 
    """
    memoire = session.service("ALMemory")
    subriber = memoire.subscriber(eventName)
    subriber.signal.connect(onEvent) # connect ne reverra rien, il faudra se débrouiller autremen si vous voulez réutiliser la valariable ailleurs

def UnSubscriber(session : Any, enventName : str) -> None:
    """
    Se désabonne à l'évènement `eventName` du robot
    
    Args:
        session: Session en cours avec le robot
        enventName: nom de l'évènement à se désabonner
    """
    
    memoire = session.service("ALMemory")
    memoire.unsubcriber(enventName)

if __name__ == '__main__' : pass