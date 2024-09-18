from abc import ABC, abstractmethod


class Message(ABC):
    def __init__(self, src=None, payload=None, dest=None, stamp=None):
        self.src = src # Le processus qui envoie le message
        self.payload = payload # Le contenu du message
        self.dest = dest # Le processus destinataire
        self.stamp = stamp # L'horloge de Lamport au moment de l'envoi


    @abstractmethod
    def process(self):
        pass