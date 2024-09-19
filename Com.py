import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from pyeventbus3.pyeventbus3 import PyBus
from Message import Message, BroadcastMessage, MessageTo, Token
from State import State

# reception et envoie ne doivent pas etre dans le fichier process, process c'est la partie utilisateur, 
# on doit seulement appeler les fonctions de communication

class Com(Thread):
    def __init__(self, process, has_token=False):
        # Appel explicite au constructeur de threading.Thread
        Thread.__init__(self)

        self.clock = 0 # Horloge de Lamport 
        self.semaphore = threading.Semaphore() # Semaphore pour la gestion des accès concurrents à l'horloge
        self.mailbox = [] # Boite aux lettres pour stocker les messages reçus
        self.process = process
        self.owner = process.name # Le processus qui utilise cette instance de Com

        # Récupérer le nombre total de processus depuis l'objet process
        self.nbProcess = process.nbProcess

        # Gestion du Token
        self.token = Token(self.owner) if has_token else None  # Initialisation du jeton si ce processus le possède
        self.process.state = State.NONE  # État initial

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

    def addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)

    # Envoie un message à tous les autres processus via le bus d'événements
    def broadcast(self, payload: object):
        
        # Incrémenter l'horloge avant d'envoyer le message
        self.inc_clock()

        # Créer un message de type BroadcastMessage
        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)

        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        # Poster le message sur le bus d'événements
        PyBus.Instance().post(message)

    # Méthode appelée lorsqu'un message broadcasté est reçu
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
    
        # Si le message n'a pas été envoyé par ce processus
        if event.src != self.owner:
            sleep(1)
            # Mettre à jour l'horloge Lamport en fonction du message reçu
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp

            # Ajouter le message à la boîte aux lettres 
            self.addMessageToMailbox(event)
            
            # Afficher le message reçu
            print(f"Process {self.owner} a reçu un message broadcasté : {self.getFirstMessage().payload}")
            sleep(1)



    # Méthode pour envoyer un message dédié à un autre processus
    def sendTo(self, payload, to):
        self.inc_clock()  # Incrémente l'horloge avant l'envoi
        messageTo = MessageTo(self.clock, payload, self.owner, to)  # Crée un message dédié

        print(f"Process {self.owner} envoie un message à {to} : {messageTo.payload} "
              f"avec timestamp {messageTo.stamp} de {messageTo.src}")

    
        PyBus.Instance().post(messageTo)  # Envoie le message via le bus

        

    # Méthode appelée lors de la réception d'un message dédié
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onMessageTo(self, event):
        if event.getReceiver() == self.owner: # Vérifie si le message est destiné à ce processus
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp
            # print(f"Process {self.owner} a reçu un message de {event.getSender()} : {event.payload}")
            self.addMessageToMailbox(event)


    # Méthode pour les tokens 
    # Demande l'accès à la session critique et bloque tant que le jeton n'est pas détenu
    def requestToken(self):
        self.process.state = State.REQUEST
        print(f"{self.owner} a demandé la section critique.")

        # Attendre jusqu'à ce que le processus passe en état SC
        while self.process.state != State.SC:
            sleep(1)


    # Libère le jeton pour permettre à un autre processus d'entrer dans la section critique
    def releaseToken(self):
        self.process.state = State.RELEASE
        print(f"{self.owner} libère le jeton.")

    # Méthode pour envoyer le jeton au processus suivant
    def sendTokenTo(self, token: Token):
    
        PyBus.Instance().post(token)
        print(f"{self.owner} a envoyé le jeton au processus {token.dest}.")


    # Token reception
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        if self.owner == event.dest and self.process.alive:
            sleep(1)
            print(f"{self.owner} a le jeton.")
            if self.process.state == State.REQUEST:
                self.process.state = State.SC
                print(f"{self.owner} entre en section critique.")
                
                # Bloquer tant que le processus n'est pas dans l'état RELEASE
                while self.process.state != State.RELEASE:
                    sleep(1)
                    print(f"{self.owner} a le jeton et l'utilise.")
                print(f"{self.owner} quitte la section critique.")

            # Extraire le numéro du propriétaire actuel (self.owner est de la forme "P2", donc on récupère "2")
            numberOwner = int(self.owner[1:])  # Récupère tout après le premier caractère
            
            # Calculer l'index du prochain processus de manière circulaire
            nextProcessNumber = (numberOwner + 1) % self.process.nbProcess
            
            # Générer le nom du prochain processus sous la forme "P" suivi du numéro
            nextProcess = "P" + str(nextProcessNumber)

            self.sendTokenTo(Token(nextProcess))
            self.process.state = State.NONE
                    