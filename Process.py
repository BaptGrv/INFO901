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
            if loop == 2 and self.name == "P0":
                self.com.synchronize()

            if loop == 4 and self.name == "P1":
                self.com.synchronize()

            if loop == 6 and self.name == "P2":
                self.com.synchronize()

            if loop == 8 and self.name == "P3":
                self.com.synchronize()





            # if self.getName() == "P0":
            #     self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
            #     self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
            #     self.com.recevFromSync(msg, 2)
               
            #     self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                    
            #     self.com.synchronize()
                    
            #     self.com.requestSC()
            #     if self.com.mailbox.isEmpty():
            #         print("Catched !")
            #         self.com.broadcast("J'ai gagné !!!")
            #     else:
            #         msg = self.com.mailbox.getMsg()
            #         print(str(msg.getSender())+" à eu le jeton en premier")
            #     self.com.releaseSC()


            # if self.getName() == "P1":
            #     if not self.com.mailbox.isEmpty():
            #         self.com.mailbox.getMessage()
            #         self.com.recevFromSync(msg, 0)

            #         self.com.synchronize()
                    
            #         self.com.requestSC()
            #         if self.com.mailbox.isEmpty():
            #             print("Catched !")
            #             self.com.broadcast("J'ai gagné !!!")
            #         else:
            #             msg = self.com.mailbox.getMsg()
            #             print(str(msg.getSender())+" à eu le jeton en premier")
            #         self.com.releaseSC()
                    
            # if self.getName() == "P2":
            #     self.com.recevFromSync(msg, 0)
            #     self.com.sendToSync("OK", 0)

            #     self.com.synchronize()
                    
            #     self.com.requestSC()
            #     if self.com.mailbox.isEmpty():
            #         print("Catched !")
            #         self.com.broadcast("J'ai gagné !!!")
            #     else:
            #         msg = self.com.mailbox.getMsg()
            #         print(str(msg.getSender())+" à eu le jeton en premier")
            #     self.com.releaseSC()
                

            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()