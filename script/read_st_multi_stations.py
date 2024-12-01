### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-07T02:30:00.000")
tf = ti + (60 * 60 * 1 * 1)  # 1 heure de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
st2 = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)

# Fusionner les données (interpolation)
st1.merge(fill_value='interpolate')
st2.merge(fill_value='interpolate')

# Detrend les signaux
st1.detrend("demean")
st1.detrend("linear")
st2.detrend("demean")
st2.detrend("linear")

# Appliquer un filtre bandpass sur les données
data1 = st1[0].data
data2 = st2[0].data
data1 = bandpass(data1, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data2 = bandpass(data2, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime
time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1) / fs, 1 / fs), unit='s'))
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2) / fs, 1 / fs), unit='s'))

# Création des subplots (3 sous-graphiques)
fig, axs = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

# 1er subplot pour la station STRA
axs[0].plot(time1, data1, color='r')
#axs[0].set_title(f"Waveform Data for Station {stz[0]}")
axs[0].set_ylabel('RSAM (counts)')
axs[0].grid(True)

# 2ème subplot pour la station STRE
axs[1].plot(time2, data2, color='b')
#axs[1].set_title(f"Waveform Data for Station {stz[1]}")
axs[1].set_ylabel('RSAM (counts)')
axs[1].grid(True)

# 3ème subplot pour les deux stations (comme précédemment)
axs[2].plot(time1, data1, label=f"{stz[0]}", color='r')
axs[2].plot(time2, data2, label=f"{stz[1]}", color='b')
#axs[2].set_title('Waveform Data for Two Stations')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('RSAM (counts)')
axs[2].legend()
axs[2].grid(True)

# Ajuster la disposition des subplots
#plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
