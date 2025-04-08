### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3'
stz = ['STRA', 'STRE', 'STRG']  # Stations STRA, STRE, STRG
net = ['I*', 'I*', 'I*']  # Tous les réseaux
channel = ['*HZ', '*HZ', '*HZ']  # Composante Z
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-03-31T01:00:00.000")
tf = ti + (60 * 60 * 4 * 1)  # 5 minutes de données

# Initialisation de dictionnaires pour stocker les données traitées
data_sismique = {}

# Récupérer les données pour chaque station (STRA, STRE, STRG)
for i, station in enumerate(stz):
    st = client.get_waveforms(network=net[i], station=station, location="", channel=channel[i], starttime=ti, endtime=tf)
    
    # Fusionner les données (interpolation)
    st.merge(fill_value='interpolate')
    
    # Detrend les signaux
    st.detrend("demean")
    st.detrend("linear")
    
    # Appliquer un filtre bandpass
    data = st[0].data
    data_sismique[station] = {}
    data_sismique[station]['raw'] = data
    data_sismique[station]['filtered'] = bandpass(data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
    data_sismique[station]['filtered_vlp'] = bandpass(data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
    
    # Créer un axe temporel pour chaque station
    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[station]['time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(0, len(data) / fs, 1 / fs), unit='s'))

# Calcul des limites (min et max) pour les 4 subplots
min_val = min(
    min(data_sismique['STRA']['filtered_vlp'].min(), data_sismique['STRA']['filtered'].min()),
    min(data_sismique['STRE']['filtered'].min(), data_sismique['STRG']['filtered'].min())
)

max_val = max(
    max(data_sismique['STRA']['filtered_vlp'].max(), data_sismique['STRA']['filtered'].max()),
    max(data_sismique['STRE']['filtered'].max(), data_sismique['STRG']['filtered'].max())
)

# Création des subplots (4 sous-graphiques)
fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True)  # Augmenter la largeur de la figure

# 1er subplot pour STRA
axs[0].plot(data_sismique['STRA']['time'], data_sismique['STRA']['filtered_vlp'], color='r', label='STRA 0.03-1Hz')
axs[0].set_ylabel('RSAM (m/s)')
axs[0].legend()
axs[0].grid(True)
axs[0].set_ylim(min_val, max_val)  # Uniformiser les limites de y

# 2ème subplot pour STRA (filtrage 0.03-24Hz)
axs[1].plot(data_sismique['STRA']['time'], data_sismique['STRA']['filtered'], color='r', label='STRA 0.03-24Hz')
axs[1].set_ylabel('RSAM (m/s)')
axs[1].legend()
axs[1].grid(True)
axs[1].set_ylim(min_val, max_val)  # Uniformiser les limites de y

# 3ème subplot pour STRE
axs[2].plot(data_sismique['STRE']['time'], data_sismique['STRE']['filtered'], color='b', label='STRE 0.03-24Hz')
axs[2].set_ylabel('RSAM (m/s)')
axs[2].legend()
axs[2].grid(True)
axs[2].set_ylim(min_val, max_val)  # Uniformiser les limites de y

# 4ème subplot pour STRG (en magenta)
axs[3].plot(data_sismique['STRG']['time'], data_sismique['STRG']['filtered'], color='magenta', label='STRG 0.03-24Hz')
axs[3].set_ylabel('RSAM (m/s)')
axs[3].legend()
axs[3].grid(True)
axs[3].set_ylim(min_val, max_val)  # Uniformiser les limites de y

# Personnaliser le format des dates sur l'axe des x pour afficher uniquement l'heure et les minutes
import matplotlib.dates as mdates
date_format = mdates.DateFormatter('%H:%M')  # Afficher uniquement l'heure et les minutes
axs[3].xaxis.set_major_formatter(date_format)

# Rotation des dates pour une meilleure lisibilité
plt.xticks(rotation=45, fontsize=12)  # Rotation des dates et taille de la police plus petite

# Ajuster l'espacement entre les subplots et l'espace pour les labels
plt.subplots_adjust(hspace=0.3)  # Augmenter l'espacement vertical entre les subplots

# Réduire la fréquence des dates affichées
axs[3].xaxis.set_major_locator(mdates.MinuteLocator(interval=2))  # Afficher une date tous les 2 minutes

# Afficher les graphiques
plt.tight_layout()  # Ajuster la disposition
plt.show()
