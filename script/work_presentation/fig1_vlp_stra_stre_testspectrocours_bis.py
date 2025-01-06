### PACKAGES
from obspy import UTCDateTime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
import matplotlib.dates as mdates
import obspy

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-07T02:53:00.000")
tf = ti + (60 * 5 * 1 * 1)  # 5 minutes de données

# Récupérer les données pour les deux stations
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
ste = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)

# Fusionner les données (interpolation)
sta.merge(fill_value='interpolate')
ste.merge(fill_value='interpolate')

# Detrend les signaux
sta.detrend("demean")
sta.detrend("linear")
ste.detrend("demean")
ste.detrend("linear")

# Appliquer un filtre bandpass sur les données
dataa = sta[0].data
datae = ste[0].data
dataa = dataa * ((3.2 * 10**(-6)) / 800)
datae = datae * ((3.2 * 10**(-6)) / 800)

# Appliquer le filtre bandpass
from obspy.signal.filter import bandpass
dataa1 = bandpass(dataa, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
datae1 = bandpass(datae, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

dataavlp = bandpass(dataa, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
dataevlp = bandpass(datae, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttimea = UTCDateTime(sta[0].stats.starttime).datetime
starttimee = UTCDateTime(ste[0].stats.starttime).datetime
timea = pd.to_datetime(starttimea + pd.to_timedelta(np.arange(0, len(dataa) / fs, 1 / fs), unit='s'))
timee = pd.to_datetime(starttimee + pd.to_timedelta(np.arange(0, len(datae) / fs, 1 / fs), unit='s'))

# Création des subplots (4 sous-graphiques)
fig, axs = plt.subplots(4, 1, figsize=(12, 15), sharex=True)

# 1er subplot pour la station STRA
axs[0].plot(timea, dataavlp, label=f"{stz[0]}", color='r')
axs[0].set_ylabel('RSAM (m/s) 0.03-1Hz')
axs[0].legend()
axs[0].grid(True)

# Calcul de la valeur maximale absolue entre les deux datasets
max_val = max(max(abs(dataa1)), max(abs(datae1)))

# 2ème subplot pour la station STRA
axs[1].plot(timea, dataa1, color='r')
axs[1].set_ylabel('RSAM (m/s) 0.03-24Hz')
axs[1].grid(True)
axs[1].set_ylim(-max_val, max_val)  # Uniformiser les limites de y

# 3ème subplot pour la station STRE
axs[2].plot(timee, datae1, color='b', label=f"{stz[1]}")
axs[2].set_ylabel('RSAM (m/s) 0.03-24Hz')
axs[2].grid(True)
axs[2].set_ylim(-max_val, max_val)  # Uniformiser les limites de y
axs[2].legend()

# 4ème subplot pour le spectrogramme de la station STRA
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
sta.merge(fill_value='interpolate')

# Vérifier si starttime est déjà un float (en secondes depuis 1970)
starttime = sta[0].stats.starttime

# Utiliser directement le timestamp comme un float
starttime_seconds = starttime.timestamp()  # Convertir en secondes depuis 1970

# Utiliser la fonction spectrogram() d'Obspy directement sur l'axe axs[3]
sta[0].spectrogram(log=True, title=f"Spectrogramme de {sta[0].stats.station}", axes=axs[3])

# Limiter la plage de fréquences
axs[3].set_ylim(0.03, 24)  # Plage souhaitée de 0.03 Hz à 24 Hz
axs[3].set_ylabel('Fréquence [Hz]')
axs[3].set_xlabel('Temps [sec]')

# Créer les labels de temps en ajoutant ces secondes au temps de départ
time_labels = pd.to_datetime(np.arange(0, len(sta[0].data) / fs, 1 / fs), unit='s') + pd.to_timedelta(starttime_seconds, unit='s')

# Formater les labels de temps
axs[3].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M:%S'))  # Format jour, mois, année, heure, minute, seconde
axs[3].set_xticks(mdates.date2num(time_labels[::int(len(time_labels)/10)]))  # Espacer les labels pour plus de lisibilité
axs[3].tick_params(axis='x', rotation=30)  # Rotation des labels pour plus de lisibilité

# Afficher la figure
plt.tight_layout()
plt.show()
