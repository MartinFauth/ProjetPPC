import sysv_ipc
from math import *
import multiprocessing as mp
import time
import socket
import signal
import random
import os
import threading as th
import queue
import struct
from statistics import mean

prixinit = 50
prixMax = 200.
prixMin = 25.
#------------------------------- Definition de la classe de Market -----------------------------------------------------

class Market(mp.Process):
    
    def __init__(self, coeff, proba, jour, NombreJour, ShMem, ThreadsNumber, maison,host,port,MarketBar):
        super().__init__()
        self.event = [0,0]
        self.coeff = coeff
        self.prixEnergie = prixinit
        self.energie_in = 0.0
        self.energie_out = 0.0
        self.coeff_gamma = 0.9998
        self.res = 0
        self.proba = proba
        self.jour = jour
        self.NombreJour = NombreJour
        self.ShMem = ShMem
        self.ThreadsNumber = ThreadsNumber
        self.maison = maison
        self.host = host
        self.port = port
        self.MarketBar = MarketBar

    def run(self):
        x = 0
        #definitions des signaux
        signal.signal(10,self.handler)
        signal.signal(30,self.handler)
        en = []
        c = 1
        while c <= self.NombreJour:
            
            en.append(round(self.prixEnergie,2))
            self.jour.wait()
            print("\n Prix de l'energie aujourd'hui : ", round(self.prixEnergie,2),"centimes\n")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.host, self.port))
                server_socket.listen(self.maison)
                self.MarketBar.wait()
                flag = True
                while flag:
        
                    client_socket, add = server_socket.accept() 
                    t = th.Thread(target = transaction, args=(self,client_socket ,add))
                    t.start()
                    t.join()
                    self.MarketBar.wait()
                    flag = False
            
                    
            ext = mp.Process(target = self.externe, args=())
            ext.start()
            ext.join()
            ext.terminate()

            #attends l'actualisation de la memoire partagee avec le process weather
            
                            


            temperature = float("{:.2f}".format(self.ShMem[1]))
            catastropheNat = float("{:.2f}".format(self.ShMem[2]))

            if catastropheNat == 1.:
                print("Catastrophe naturelle")
            
            n = len(self.event)
            for i in range(n):
                x += self.coeff[i+2]*self.event[i]
                
            
            
            
            evntinterne = ( 1/temperature ) * self.coeff[0] - self.res*self.coeff[-1]
            
            # Si l'evenement est realise : vaut 1, sinon vaut 0
            evtexterne = x + catastropheNat * self.coeff[1]
            
            self.prixEnergie = self.prixEnergie*self.coeff_gamma + evntinterne + evtexterne
            
                        
            if self.prixEnergie >= prixMax:
                self.prixEnergie = prixMax
            elif self.prixEnergie <= prixMin:
                self.prixEnergie = prixMin
            

            c += 1         
            self.jour.wait()
            self.event = [0,0]
            self.res = 0
            x = 0 
        print("\n Ce mois-ci, le prix moyen de l'electricite est de : ",round(mean(en),2),"centimes\n")


#------------------------------------Definition des diffÃ©rentes fonctions utilisÃ©es ------------------------------------------------------

    def handler(self, sig, frame):
        if sig == 10:
            self.event[0] = 1
            print("--------------------- Guerre --------------------------")
        elif sig == 30:
            self.event[1] = 1
            print("\n--------------------- Inflation ------------------------")

    def externe(self):
        signals = [10,30]
        p = len(self.proba)
        
        for i in range(p):
            if (random.randint(1,int( 1/self.proba[i] ))) == 1 :
                os.kill(os.getppid(),signals[i])
        

def transaction(self, s, a):
    data = s.recv(1024)
    nrj = struct.unpack("f",data)                
    if nrj[0] < 0:
        self.energie_out += abs(nrj[0])
    else:    
        self.energie_in += nrj[0]
    s.close()
    self.res += nrj[0]