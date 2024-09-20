from threading import Lock, Thread

from time import sleep
import time
from Message import Token

from Com import Com

class Process(Thread):
    
    def __init__(self,name, nbProcess):
        Thread.__init__(self)

        self.nbProcess = nbProcess
        self.name = name
        self.com = Com(self)

        self.setName(name)


        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)
            
            # Exemple d'utilisation de broadcast
            # if loop == 2:  # Envoyer un message à tout le monde au 2e tour
            #     if self.getName() == "P0":
            #         self.com.broadcast("Bonjour de la part de P0")

        
            # Exemple d'utilisation de sendTo
            # if loop == 2 and self.name == "P0":
            #     self.com.sendTo("Bonjour","P1")
            # if loop == 4 and self.name == "P1":
            #     if len(self.com.mailbox) > 0:
            #         print(f"{self.name} a reçu un message : {self.com.getFirstMessage().payload}")


            # Exemple d'utilisation de Token
            # Demande l'accès à la section critique
            
            # if loop == 1 and self.name == "P0":
            #     t = Token("P1")
            #     self.com.sendTokenTo(t)

            # if loop == 2 and self.name == "P2":
            #     self.com.requestToken()
            #     print("enterin CS")
            #     sleep(2)
            #     print("leaving CS")
            #     self.com.releaseToken()

            # if loop == 3 and self.name == "P1":
            #     self.com.requestToken()
            #     print("enterin CS")
            #     sleep(2)
            #     print("leaving CS")
            #     self.com.releaseToken()
            

            # Exemple d'utilisation de Synchronisation
            # Synchronize test
            # if loop == 2 and self.name == "P0":
            #     self.com.synchronize()

            # if loop == 4 and self.name == "P1":
            #     self.com.synchronize()

            # if loop == 5 and self.name == "P2":
            #     self.com.synchronize()

            # if loop == 6 and self.name == "P3":
            #     self.com.synchronize()



            # Exemple d'utilisation de Broadcast Synchronisé
            # if loop == 1 and self.name == "P0":
            #     self.com.broadcastSync(self.name, "Bonjour tout le monde")

            # if loop == 4 and self.name == "P2":
            #     self.com.broadcastSync(self.name, "Moi aussi j'envoie un message")

             
            # Exemple d'utilisation de MessageToSync
            # if loop == 2 and self.name == "P0":
            #     self.com.sendToSync("Bonjour de la part de P0", "P1")

            # if loop == 4 and self.name == "P1":
            #     self.com.receivFromSync()

            # if loop == 5 and self.name == "P2":
            #     self.com.receivFromSync()
            
            # if loop == 6 and self.name == "P3":
            #     self.com.receivFromSync()

            # if loop == 8 and self.name == "P0":
            #     self.com.sendToSync("Bonjour de la part de P0", "P2")
            
            # if loop == 10 and self.name == "P1":
            #     self.com.sendToSync("Bonjour de la part de P1", "P3")
    
        
            # Test de diffusion broadcast
            if loop == 2 and self.name == "P0":
                self.com.broadcast("Bonjour de la part de P0")
            
            if loop == 3:
                if len(self.com.mailbox) > 0:
                    print(f"{self.name} a reçu un message broadcasté : {self.com.getFirstMessage().payload}")

            # Test de message dédié synchrone
            if loop == 4 and self.name == "P0":
                self.com.sendToSync("Message dédié de P0 à P1", "P1")
            
            if loop == 6 and self.name == "P1":
                self.com.receivFromSync()

            if loop == 8 and self.name == "P1":
                if len(self.com.mailbox) > 0:
                    print(f"{self.name} a reçu un message dédié : {self.com.getFirstMessage().payload}")

            # Test de Token et section critique
            if loop == 9 and self.name == "P0":
                t = Token("P1")
                self.com.sendTokenTo(t)
            
            if loop == 10 and self.name == "P1":
                self.com.requestToken()
                print(f"{self.name} entre en section critique")
                sleep(2)
                print(f"{self.name} quitte la section critique")
                self.com.releaseToken()
            
            if loop == 12 and self.name == "P2":
                self.com.requestToken()
                print(f"{self.name} entre en section critique")
                sleep(2)
                print(f"{self.name} quitte la section critique")
                self.com.releaseToken()

            # Test de synchronisation
            if loop == 14 and self.name == "P0":
                self.com.synchronize()

            if loop == 16 and self.name == "P1":
                self.com.synchronize()

            if loop == 18 and self.name == "P2":
                self.com.synchronize()

            if loop == 20 and self.name == "P3":
                self.com.synchronize()




            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()