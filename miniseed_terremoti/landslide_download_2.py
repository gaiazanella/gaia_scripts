### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
from obspy import read


# Paramètres de récupération des données
db = '/mnt/bigmama3'  # Chemin vers le répertoire de données
stz = ['STR*']  # Liste des stations (exemple)
net = ['I*']  # Liste des réseaux (exemple)
channel = ['*HZ']  # Liste des canaux (exemple)

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-06T08:57:00.000")  # Heure de début
tf = ti + (60 * 4 * 1)  # Heure de fin (20 minutes après)

# Récupérer les données de la station spécifiée
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
st1.merge()  # Fusionner les traces si elles sont séparées

# Diviser le Stream en traces séparées et appliquer un detrend
st1 = st1.split()
for trace in st1:
    trace.detrend("demean")  # Retirer la moyenne
    trace.detrend("linear")  # Retirer la tendance linéaire

# Afficher les données après traitement
st1.plot()

# Enregistrer le stream dans un fichier .mseed
output_path = '/home/gaia/Documents/mseed_landslide/mseed_lds_catalog/20201006_08.55.mseed'
st1.write(output_path, format='MSEED')  # Enregistrer au format MiniSEED

print(f"Fichier enregistré sous {output_path}")

# Lire à nouveau pour vérifier
traces = read(output_path)
print("Fichier MiniSEED chargé :", traces)

# Afficher un graphique de la première trace pour vérifier visuellement
traces[0].plot()

# Afficher des informations détaillées sur la première trace
print("Station:", traces[0].stats.station)
print("Canal:", traces[0].stats.channel)
print("Temps de début:", traces[0].stats.starttime)
print("Temps de fin:", traces[0].stats.endtime)
print("Données:", traces[0].data)
