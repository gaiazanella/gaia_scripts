import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-07T02:53:00.000")
tf = ti + (60 * 5 * 1 * 1)  # 1 heure de données

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
dataa1 = bandpass(dataa, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
datae1 = bandpass(datae, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

dataavlp = bandpass(dataa, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
dataevlp = bandpass(datae, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttimea = UTCDateTime(sta[0].stats.starttime).datetime
starttimee = UTCDateTime(ste[0].stats.starttime).datetime
timea = pd.to_datetime(starttimea + pd.to_timedelta(np.arange(0, len(dataa) / fs, 1 / fs), unit='s'))
timee = pd.to_datetime(starttimee + pd.to_timedelta(np.arange(0, len(datae) / fs, 1 / fs), unit='s'))

# Calculer la valeur maximale absolue entre les deux datasets
max_val = max(max(abs(dataa1)), max(abs(datae1)))

# 4 sous-graphiques partagés en x (avec une taille uniforme)
fig, axs = plt.subplots(4, 1, figsize=(12, 15), sharex=True)

# 1er subplot pour les stations STRA et STRE
axs[0].plot(timea, dataavlp, label=f"{stz[0]}", color='r')
axs[0].plot(timee, dataevlp, label=f"{stz[1]}", color='b')
axs[0].set_ylabel('RSAM (m/s) 0.03-1Hz')
axs[0].legend()
axs[0].grid(True)
axs[0].set_ylim(-max_val, max_val)  # Limites de l'axe y ajustées pour ne pas être trop dézoomé

# 2ème subplot pour la station STRA
axs[1].plot(timea, dataa1, color='r')
axs[1].set_ylabel('RSAM (m/s) 0.03-24Hz')
axs[1].grid(True)
axs[1].set_ylim(-max_val, max_val)  # Uniformiser les limites de y

# 3ème subplot pour la station STRE
axs[2].plot(timee, datae1, color='b')
axs[2].set_ylabel('RSAM (m/s) 0.03-24Hz')
axs[2].grid(True)
axs[2].set_ylim(-max_val, max_val)  # Uniformiser les limites de y

# 4ème subplot pour le spectrogramme de la station STRA
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
sta.merge(fill_value='interpolate')

# Calcul du spectrogramme
# Nous allons ici calculer les valeurs de temps en fonction des indices
time_spectrogram = pd.to_datetime(starttimea + pd.to_timedelta(np.arange(0, len(sta[0].data)) / fs, unit='s'))

# Calcul du spectrogramme
Pxx, freqs, bins, im = axs[3].specgram(sta[0].data, NFFT=256, Fs=sta[0].stats.sampling_rate, noverlap=192, cmap='viridis')

# Limiter la plage de fréquences dans le spectrogramme
axs[3].set_ylim(0.03, 24)  # Plage souhaitée de 0.03 Hz à 24 Hz

# Ajouter des labels sans titre sur le spectrogramme
axs[3].set_ylabel('Fréquence [Hz]')
axs[3].set_xlabel('Temps [s]')

# Aligner l'axe des X du spectrogramme avec les autres subplots
axs[3].set_xticks(np.linspace(0, len(sta[0].data), 7))  # Choisir 7 points pour les ticks
axs[3].set_xticklabels(time_spectrogram[::len(sta[0].data) // 7].strftime('%H:%M:%S'), rotation=45)  # Formater les labels

# Définir les mêmes limites d'axe X pour tous les subplots
axs[0].set_xlim(timea.min(), timea.max())
axs[1].set_xlim(timea.min(), timea.max())
axs[2].set_xlim(timee.min(), timee.max())
axs[3].set_xlim(timea.min(), timea.max())  # Le spectrogramme utilise aussi les mêmes limites

# Ajuster la mise en page pour éviter que les sous-graphiques se chevauchent
plt.tight_layout()

# Afficher la figure complète avec les 4 subplots
plt.show()
