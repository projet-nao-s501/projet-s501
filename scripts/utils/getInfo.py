from typing import Any


def GetEvenements(session : Any) -> None :

    memoire = session.service("ALMemory")
    for i in memoire.getEventList() :
        print(f"{i} \n")

def GetAllMethodes(session : Any, nomService : str) -> None :
    
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