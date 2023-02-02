import threading as th
import multiprocessing as ms
import signal
import os
import queue
import sysv_ipc
import sys
import time
import random
import math
from weather import Weather
from market import Market
from home import Home


HOST = "localhost"
PORT = 6954


#Memoire partagee : [0] Temperature, [1] Catastrophe Naturelle

if __name__ == "__main__":

    try:

        print("--------Simulation du marché de l'énergie--------")

        ShMem = ms.Array('f',4)
        nbrJour = 30
        nbrHome = 5
        initTemp = 30.0
        tendance = 1.0 #tendance (1.0 = augmentation, -1.0 = diminution)

        nbrThreads= 5
        Jour = ms.Barrier(nbrHome+2)
        homesBar = ms.Barrier(nbrHome)
        MarketBar = ms.Barrier (nbrHome+1)
        Lock = ms.Lock()

        #Proba catastrophe nat
        probaH = math.pow(10,-1)
        #[proba Guerre, proba Inflation]
        probaEP = [math.pow(10,-4),math.pow(10,-2)]


        #coeff = [Temperature,Catastrophe Naturelle,Guerre, Inflation, transaction]
        coeff = [0.5,7.5,10,1.5,2]

        #Creation de Queues pour la communications inter-foyer (Maison-Maison)
        homeGive = ms.Queue(nbrHome)
        homereceive = ms.Queue(nbrHome)

        #Processes creation
        weather_process = Weather(probaH, ShMem, Jour, nbrJour, initTemp)
        
        market_process = Market( coeff, probaEP, Jour, nbrJour, ShMem, nbrThreads, nbrHome,HOST,PORT,MarketBar)

        homes_processes = [Home(i+1, homeGive, homereceive, Jour, homesBar, Lock, nbrJour,HOST,PORT,MarketBar) for i in range (nbrHome)]

        #Processes Start
        weather_process.start()
        market_process.start()
        for process in homes_processes :
            process.start()

        #Processes Join
        weather_process.join()
        market_process.join()
        for process in homes_processes :
            process.join()

        #Processes Terminate
        weather_process.terminate()
        market_process.terminate()
        for process in homes_processes :
            process.terminate()

    #Si jamais Ctrl+C
    except KeyboardInterrupt:
        weather_process.terminate()
        market_process.terminate()
        for process in homes_processes :
            process.terminate()

    print("--------Fin de simulation--------")