import multiprocessing as mp
import random
import time


tempMax = 36.55
tempMin = 0.05
#---------------------------------------Creation de la class weather-----------------------------------

class Weather(mp.Process):

    def __init__(self,probaCatastropheNat, ShMem, jour, NombreJour, temperature):
        super().__init__()
        self.probaCatastropheNat = probaCatastropheNat
        self.ShMem = ShMem
        self.jour = jour
        self.NombreJour = NombreJour
        self.temperature = temperature

# --------------------- Definition de la fonction qui change la météo selon le jour------------------------------
    def run(self):

        self.ShMem[1] = self.temperature
        c = 1
        while c <= self.NombreJour:
            self.way = random.choice([-1,1])
            self.temperature += self.way*random.random()*2
            print("\n ----------------------------------------------------------------\nJour",c," et il fait", round(self.temperature-10,2), "°C \n")
            
            self.ShMem[2] = self.ShMem[3]=0.0

            self.ShMem[0] = float("{:.2f}".format(self.ShMem[1]))
            self.ShMem[1] = self.temperature 
            r = random.randint(1,int((1/self.probaCatastropheNat)))
            if r == 1:
                self.ShMem[2] = 1.
            
            c += 1
            self.jour.wait()      
            self.jour.wait()    