### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
from obspy import read

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STR*']
net = ['I*']
channel = ['*H*']

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2022-10-08:22:02.000")
tf = ti + (60 * 25 * 1)  # 20 min de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
#print(st1)
st1.write('/home/gaia/Documents/mseed_terremoti/20221008_M5.2.mseed')
#st1.write('/home/gaia/Documents/mseed_terremoti/20221109_M5.6.mseed')
st1.plot()
# Chemin vers ton fichier MiniSEED
#mseed_file = '/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed'

# Lire le fichier MiniSEED
#st = read(mseed_file)

# Afficher les informations sur les traces (métadonnées)
#print(st)

# Optionnel : Tracer le premier trace pour vérifier visuellement
#st[0].plot()