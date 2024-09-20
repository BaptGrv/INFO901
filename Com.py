import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from pyeventbus3.pyeventbus3 import PyBus
from Message import Message, BroadcastMessage, MessageTo, Token, SynchronizationMessage, BroadcastMessageSync, MessageToSync, ReceivedMessageSync
from State import State



class Com(Thread):
    """
    Classe Communicator (Com) qui gère la communication entre les processus via un bus d'événements
    et utilise une horloge de Lamport pour la synchronisation des événements.

    Attributs:
    - process (Process): Le processus auquel ce communicateur est associé.
    - clock (int): L'horloge logique de Lamport utilisée pour la synchronisation.
    - semaphore (Semaphore): Utilisé pour gérer les accès concurrents à l'horloge.
    - mailbox (list): Liste des messages reçus par le processus.
    - nbProcess (int): Le nombre total de processus dans le système.
    - token (Token): Jeton utilisé pour la section critique si ce processus en possède un.
    - messageReceived (bool): Indique si un message a été reçu.
    """


    def __init__(self, process, has_token=False):
        """
        Initialise le communicateur pour un processus.

        :param process: L'objet Process associé à ce communicateur.
        :param has_token: Indique si ce processus possède le jeton initial.
        """

        Thread.__init__(self)
        self.clock = 0 # Horloge de Lamport 
        self.semaphore = threading.Semaphore() # Semaphore pour la gestion des accès concurrents à l'horloge
        self.mailbox = [] # Boite aux lettres pour stocker les messages reçus
        self.process = process
        self.owner = process.name # Le processus qui utilise cette instance de Com

        # Récupérer le nombre total de processus depuis l'objet process
        self.nbProcess = process.nbProcess

        self.cptSynchronize = self.nbProcess - 1  # Compteur pour la synchronisation
        self.messageReceived = False  # Indique si un message a été reçu

        # Gestion du Token
        self.token = Token(self.owner) if has_token else None  # Initialisation du jeton si ce processus le possède
        self.process.state = State.NONE  # État initial

        PyBus.Instance().register(self, self)


    def inc_clock(self):
        """
        Incrémente l'horloge logique de Lamport pour ce processus.

        :return: La nouvelle valeur de l'horloge.
        """
        with self.semaphore:
            self.clock += 1
            return self.clock
        
    def get_clock(self):
        """
        Retourne la valeur actuelle de l'horloge logique de Lamport.

        :return: La valeur de l'horloge.
        """
        return self.clock
    
    # Gestion de la boite aux lettres
    def addMessageToMailbox(self, msg: Message):
        """
        Ajoute un message à la boîte aux lettres du processus.

        :param msg: Le message à ajouter.
        """
        self.mailbox.append(msg)

    def getFirstMessage(self) -> Message:
        """
        Retourne et retire le premier message de la boîte aux lettres.

        :return: Le premier message de la boîte aux lettres.
        """
        return self.mailbox.pop(0)


    def broadcast(self, payload: object):
        """
        Envoie un message à tous les autres processus via le bus d'événements.

        :param payload: Le contenu du message à envoyer.
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
        Méthode appelée lorsqu'un message broadcasté est reçu.

        :param event: L'événement de diffusion du message.
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
            self.addMessageToMailbox(event)
            
            # Afficher le message reçu
            print(f"Process {self.owner} a reçu un message broadcasté : {self.getFirstMessage().payload}")
            sleep(1)




    def sendTo(self, payload, to):
        """
        Envoie un message dédié à un autre processus via le bus d'événements.

        :param payload: Le contenu du message.
        :param to: Le destinataire du message.
        """
        self.inc_clock()  # Incrémente l'horloge avant l'envoi
        messageTo = MessageTo(self.clock, payload, self.owner, to)  # Crée un message dédié

        print(f"Process {self.owner} envoie un message à {to} : {messageTo.payload} "
              f"avec timestamp {messageTo.stamp} de {messageTo.src}")

    
        PyBus.Instance().post(messageTo)  # Envoie le message via le bus

        


    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onMessageTo(self, event):
        """
        Méthode appelée lors de la réception d'un message dédié.

        :param event: L'événement MessageTo représentant le message reçu.
        """
        if event.getReceiver() == self.owner: # Vérifie si le message est destiné à ce processus
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp
            # print(f"Process {self.owner} a reçu un message de {event.getSender()} : {event.payload}")
            self.addMessageToMailbox(event)


    # Méthode pour les tokens 

    def requestToken(self):
        """
        Demande l'accès à la section critique et bloque tant que le jeton n'est pas détenu.
        """
        self.process.state = State.REQUEST
        print(f"{self.owner} a demandé la section critique.")

        # Attendre jusqu'à ce que le processus passe en état SC
        while self.process.state != State.SC:
            sleep(1)


    def releaseToken(self):
        """
        Libère le jeton pour permettre à un autre processus d'entrer dans la section critique.
        """
        self.process.state = State.RELEASE
        print(f"{self.owner} libère le jeton.")


    def sendTokenTo(self, token: Token):
        """
        Envoie le jeton au processus suivant.

        :param token: Le jeton à envoyer.
        """
        PyBus.Instance().post(token)
        print(f"{self.owner} a envoyé le jeton au processus {token.dest}.")


    # Token reception
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        """
        Méthode appelée lors de la réception d'un jeton.
        """
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

    # Méhode pour la synchronisation
    def synchronize(self):
        """
        Synchronise le processus avec les autres en atteignant un point de synchronisation.
        """
        PyBus.Instance().post(SynchronizationMessage(src=self.owner, stamp=self.clock))
        print(f"{self.owner} a atteint le point de synchronisation.")

        while self.cptSynchronize > 0:
            sleep(1)

        # Réinitialiser le compteur pour la prochaine synchronisation
        self.cptSynchronize = self.process.nbProcess - 1


    @subscribe(threadMode=Mode.PARALLEL, onEvent=SynchronizationMessage)
    def onSynchronize(self, event):
        """
        Méthode appelée lors de la réception d'un message de synchronisation.
        """

        if event.src != self.owner:
            self.cptSynchronize -= 1

    

    ############Méthodes synchrones################

    # Méthode broadcast synchrone
    def broadcastSync(self,sender, payload):
        """
        Méthode de diffusion synchrone.
        
        :param sender: Le processus émetteur.
        :param payload: Le message à diffuser.
        """
        if self.owner == sender:
            self.inc_clock()
            messageSync = BroadcastMessageSync(src=self.owner, payload=payload, stamp=self.clock)
            PyBus.Instance().post(messageSync)
            print(f"Process {self.owner} envoie un message broadcasté : {payload}")
            self.synchronize()
        else:
            while not self.messageReceived:
                sleep(1)
            self.synchronize()
            self.messageReceived = False
                    

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcast(self, event):
        """
        Méthode appelée lors de la réception d'un message broadcast synchrone.

        :param event: L'événement de diffusion synchrone.
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
            self.addMessageToMailbox(event)
            
            # Afficher le message reçu
            print(f"Process {self.owner} a reçu un message broadcasté : {self.getFirstMessage().payload}")
            self.synchronize()
            self.messageReceived = True



    def sendToSync(self, payload, to):
        """
        Envoie un message dédié à un autre processus en mode synchrone.

        :param payload: Le message à envoyer.
        :param to: Le destinataire du message.
        """
        self.inc_clock()  # Incrémente l'horloge avant l'envoi
        messageToSync = MessageToSync(self.clock, payload, self.owner, to)

        print(f"Process {self.owner} envoie un message à {to} : {messageToSync.payload} ")
    
        PyBus.Instance().post(messageToSync)  # Envoie le message via le bus

        while not self.messageReceived:
            sleep(1)
        self.messageReceived = False

    # Méthode appelée lors de la réception d'un message dédié synchronisé
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageToSync)
    def onMessageToSync(self, event):
        if event.receiver == self.owner: # Vérifie si le message est destiné à ce processus
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp
            # print(f"Process {self.owner} a reçu un message de {event.getSender()} : {event.payload}")
            self.messageReceived = True
            self.addMessageToMailbox(event)


    # Méthode pour attendre la réception d'un message
    def receivFromSync(self):
        """
        Méthode pour attendre la réception d'un message synchrone.
    
        :raises: La méthode bloque tant qu'aucun message n'est reçu.
        """
        print(f"{self.owner} attend un message.")
        while not self.messageReceived :
            sleep(1)
        lastMessage = self.mailbox[len(self.mailbox) - 1]
        receiveMsg = ReceivedMessageSync(src=self.owner, stamp=self.clock, receiver=lastMessage.src)
        PyBus.Instance().post(receiveMsg)
        self.messageReceived = False

    @subscribe(threadMode=Mode.PARALLEL, onEvent=ReceivedMessageSync)
    def onReceivFromSync(self, event):
        """
        Méthode appelée lors de la réception d'un accusé de réception (`ReceivedMessageSync`).

        :param event: L'événement de type `ReceivedMessageSync` contenant l'accusé de réception.
        """
        if event.receiver == self.owner:
            print("Message reçu")
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.messageReceived = True
