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
channel = ['*HZ']

# Client pour récupérer les données
client = Client(db)
#ti = UTCDateTime("2020-03-23:19:02.000")
#tf = ti + (60 * 2 * 1)  # 20 min de données

# Heure de début précise à 19:02
ti = UTCDateTime("2024-08-01T19:41:00.000")

# Heure de fin précise à 19:04
tf = UTCDateTime("2024-08-01T19:48:00.000")

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
st1.merge()

# Diviser le Stream en traces sans valeurs masquées
st1 = st1.split()

# Appliquer un detrend sur chaque trace séparée
for trace in st1:
    trace.detrend("demean")  # Met le signal autour de zéro
    trace.detrend("linear")  # Retirer une tendance linéaire

# Afficher le stream prétraité
st1.plot()

#st1.merge()
#st1.detrend("demean") #met le signal autour de zéro 
#st1.detrend("linear") 
#print(st1)

#st1.write('/home/gaia/Documents/mseed_landslide/mseed_landslide_test/20200323_10.08.mseed')
#st1.plot()

# Chemin vers ton fichier MiniSEED
#mseed_file = '/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed'

# Lire le fichier MiniSEED
#st = read(mseed_file)

# Afficher les informations sur les traces (métadonnées)
#print(st)

# Optionnel : Tracer le premier trace pour vérifier visuellement
#st[0].plot()

