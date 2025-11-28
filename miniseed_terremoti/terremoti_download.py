### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
from obspy import read

# Paramètres
db = '/mnt/bigmama3'
stz = ['STR*']
net = ['I*']
channel = ['*HZ']

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-04-04T10:00:00.000")
#tf = ti + (60 * 20 * 1)  # 20 min de données
tf = UTCDateTime("2020-04-04T11:00:00.000")

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)

print(st1)
#print(st1)
#st1.write('/home/gaia/Documents/mseed_terremoti/20221008_M5.2.mseed')
st1.write('/home/gaia/Documents/mseed_terremoti/miniseed_terremoti_selected/z_composant/20250207.mseed')
st1.plot()
# Chemin vers ton fichier MiniSEED
#mseed_file = '/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed'

# Lire le fichier MiniSEED
#st = read(mseed_file)

# Afficher les informations sur les traces (métadonnées)
#print(st)

# Optionnel : Tracer le premier trace pour vérifier visuellement
#st[0].plot()