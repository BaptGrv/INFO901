import threading

from pyeventbus3.pyeventbus3 import *

# reception et envoie ne doivent pas etre dans le fichier process, process c'est la partie utilisateur, 
# on doit seulement appeler les fonctions de communication

class Com:
    def __init__(self):
        self.clock = 0 # Horloge de Lamport 
        self.semaphore = threading.Semaphore() # Semaphore pour la gestion des accès concurrents à l'horloge


    # Incrémente l'horloge de Lamport
    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock
        
    def get_clock(self):
        return self.clock
    
   #