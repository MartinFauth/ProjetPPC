import threading as threading
import multiprocessing as ms
import socket
import signal
import os
import queue
import sysv_ipc
import sys
import time
import random
import math
import struct




#----------------------------------------------------Creation de la classe Home--------------------------------------------------------------------

class Home(ms.Process):
    
    def __init__(self,n,homeGive,homeRecieve, jour, homesBar, Lock, nbrJour,host,port,MarketBar):
        super().__init__()
        self.number = n
        self.prod = random.random()
        self.cons = random.random()
        self.pol = random.randrange(0,3)
        self.energyQuan = self.prod - self.cons
        self.homeGive=homeGive
        self.homeRecieve = homeRecieve
        self.Lock = Lock
        self.homesBar = homesBar
        self.jour = jour
        self.nbrJour = nbrJour
        self.host = host
        self.port = port
        self.MarketBar = MarketBar

#---------------------------------------------------------------Definition des fonctions-------------------------------------------

    def run(self):
        
        i = 1
        
        
        while i <= self.nbrJour:
            
            self.jour.wait()
            self.MarketBar.wait()


            if self.cons >= 1.0:
                self.cons = 1-0.000001
            if self.cons < 0.0:
                self.cons = 0.0

            self.energyQuan = self.prod - self.cons
            if self.energyQuan > 0.0 and self.pol !=0:

                self.depot()
                self.homesBar.wait()
                self.makeHome(self.energyQuan, 'donne {:.3f} d\'énergie gratuite.'.format(self.energyQuan))
                self.homesBar.wait()
                self.verification()
                
                


                if self.energyQuan > 0. and self.pol == 2:
                    self.envoi()
                    self.makeHome(0, 'a vendu {:.3f} d\'énergie au marché.'.format(self.energyQuan))
                    self.energyQuan=0
                    

                elif self.energyQuan > 0. and self.pol == 1:

                    self.makeHome(0, 'a jeté {:.3f} d\'énergie.'.format(self.energyQuan))
                    self.energyQuan=0.
            
            elif self.energyQuan> 0.0 and self.pol == 0:
                
                self.envoi()
                self.makeHome(0, 'vend {:.3f} d\'énergie au marché.'.format(self.energyQuan))
                self.energyQuan = 0.
                self.homesBar.wait()
                self.homesBar.wait()
                

            elif self.energyQuan<0:
                self.makeHome(self.energyQuan, 'manque d\'énergie.')
                self.homesBar.wait()
                self.Lock.acquire()
                n = self.homeGive.qsize()
                for _ in range(n):
                    quantite = self.homeGive.get()
                    if self.energyQuan + quantite >= 0. and not self.homeRecieve.full():
                        self.energyQuan= 0.
                        self.makeHome(self.energyQuan,'a pris {:.3f} d\'énergie gratuite'.format(quantite))
                    else:
                        self.homeGive.put(quantite)
                if self.energyQuan < 0.:
                    self.envoi()
                    self.makeHome(0, ' achète {:.3f} d\'énergie au marché'.format(-self.energyQuan))
                    self.energyQuan= 0.
                    
                self.Lock.release()
                self.homesBar.wait()

            
            if self.number == 1:
                vider_queue(self.homeGive)
                vider_queue(self.homeRecieve)

            i += 1
            self.MarketBar.wait()
            self.jour.wait()
            self.cons = random.random()

    def depot(self):
        self.Lock.acquire()
        self.homeGive.put(self.energyQuan)
        self.Lock.release()

    def envoi(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            nrjbytes = struct.pack("f",self.energyQuan)
            client_socket.send(nrjbytes)

    def verification(self):
        self.Lock.acquire()
        if not self.homeRecieve.empty():
            for _ in range (self.homeRecieve.qsize()):
                quant = self.homeRecieve.get()
                if quant == self.energyQuan:
                    self.makeHome(0, 'donne {:.3f} d\'énergie gratuite', format(self.energyQuan))
                    self.energyQuan= 0.
                else:
                    self.homeRecieve.put(quant)
        self.Lock.release()


    def makeHome(self, energy, s):
        a =float("{:.2f}".format(self.prod))
        b =float("{:.2f}".format(self.cons))
        c = float("{:.2f}".format(energy))
        print("Maison n°",self.number, '([',self.pol,'],',a,',',b,',{',c,'})',s,sep="")


def vider_queue(q):
    if not q.empty():
        _ = q.get()
        vider_queue(q)