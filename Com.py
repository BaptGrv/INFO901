import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from pyeventbus3.pyeventbus3 import PyBus
from Message import Message, BroadcastMessage

# reception et envoie ne doivent pas etre dans le fichier process, process c'est la partie utilisateur, 
# on doit seulement appeler les fonctions de communication

class Com(Thread):
    def __init__(self, process):
        self.clock = 0 # Horloge de Lamport 
        self.semaphore = threading.Semaphore() # Semaphore pour la gestion des accès concurrents à l'horloge
        self.mailbox = [] # Boite aux lettres pour stocker les messages reçus
        self.owner = process.name # Le processus qui utilise cette instance de Com
        self.process = process 

        PyBus.Instance().register(self, self)

    # Incrémente l'horloge de Lamport
    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock
        
    def get_clock(self):
        return self.clock
    
    # Gestion de la boite aux lettres
    def getFirstMessage(self) -> Message:
        return self.mailbox.pop(0)

    def __addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)

    def broadcast(self, payload: object):
        """
        Envoie un message à tous les autres processus via le bus d'événements
        """
        # Incrémenter l'horloge avant d'envoyer le message
        self.inc_clock()

        # Créer un message de type BroadcastMessage
        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)

        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        # Poster le message sur le bus d'événements
        PyBus.Instance().post(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
        Lire un message broadcasté sur le bus
        """
        # Si le message n'a pas été envoyé par ce processus
        if event.src != self.owner:
            sleep(1)
            # Mettre à jour l'horloge Lamport en fonction du message reçu
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp

            # Ajouter le message à la boîte aux lettres 
            self.__addMessageToMailbox(event)
            
            # Afficher le message reçu
            print(f"Process {self.owner} a reçu un message broadcasté : {event.payload}")
            sleep(1)
