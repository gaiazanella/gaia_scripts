### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE', 'STRG', 'STRC']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-21T22:00:00.000")
tf = ti + (60 * 60 * 2 * 1)  # 1 heure de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
st2 = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)
st3 = client.get_waveforms(network=net[0], station=stz[2], location="", channel=channel[1], starttime=ti, endtime=tf)
st4 = client.get_waveforms(network=net[1], station=stz[3], location="", channel=channel[1], starttime=ti, endtime=tf)

# Fusionner les données (interpolation)
st1.merge(fill_value='interpolate')
st2.merge(fill_value='interpolate')
st3.merge(fill_value='interpolate')
st4.merge(fill_value='interpolate')

# Detrend les signaux
st1.detrend("demean")
st1.detrend("linear")
st2.detrend("demean")
st2.detrend("linear")
st3.detrend("demean")
st3.detrend("linear")
st4.detrend("demean")
st4.detrend("linear")

# Appliquer un filtre bandpass sur les données
data1 = st1[0].data
data2 = st2[0].data
data3 = st3[0].data
data4 = st4[0].data
data1 = bandpass(data1, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data2 = bandpass(data2, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data3 = bandpass(data1, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data4 = bandpass(data2, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime
starttime3 = UTCDateTime(st1[0].stats.starttime).datetime
starttime4 = UTCDateTime(st2[0].stats.starttime).datetime
time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1) / fs, 1 / fs), unit='s'))
print(time1)
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2) / fs, 1 / fs), unit='s'))
time3 = pd.to_datetime(starttime3 + pd.to_timedelta(np.arange(0, len(data3) / fs, 1 / fs), unit='s'))
time4 = pd.to_datetime(starttime4 + pd.to_timedelta(np.arange(0, len(data4) / fs, 1 / fs), unit='s'))

# Création des subplots (3 sous-graphiques)
fig, axs = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

# 1er subplot pour la station STRA
axs[0].plot(time1, data1, color='r', label="STRA")
#axs[0].set_title(f"Waveform Data for Station {stz[0]}")
axs[0].set_ylabel('RSAM (counts)')
axs[0].grid(True)
axs[0].legend()

# 2ème subplot pour la station STRE
axs[1].plot(time2, data2, color='b', label="STRE")
#axs[1].set_title(f"Waveform Data for Station {stz[1]}")
axs[1].set_ylabel('RSAM (counts)')
axs[1].grid(True)
axs[1].legend()

# 3ème subplot pour les deux stations (comme précédemment)
axs[2].plot(time3, data3, color='magenta', label="STRG")
#axs[1].set_title(f"Waveform Data for Station {stz[1]}")
axs[2].set_ylabel('RSAM (counts)')
axs[2].grid(True)
axs[2].legend()

# 3ème subplot pour les deux stations (comme précédemment)
axs[3].plot(time4, data4, color='black', label="STRC")
#axs[1].set_title(f"Waveform Data for Station {stz[1]}")
axs[3].set_ylabel('RSAM (counts)')
axs[3].grid(True)
axs[3].legend()

# Ajuster la disposition des subplots
#plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
