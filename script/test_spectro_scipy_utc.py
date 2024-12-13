import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
from scipy import signal
import pandas as pd  # Ajout de l'importation de pandas

# Paramètres
db = '/mnt/bigmama3/miniseed'  # Chemin vers la base de données SDS
stz = ['STRA', 'STRE']  # Station STRA
net = ['I*', 'I*']  # Réseau
channel = ['*HZ', '*HZ']  # Canal
fs = 50  # Fréquence cible (en Hz)

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-10-07T02:53:00.000")  # Temps de début
tf = ti + (60 * 60 * 1 * 1)  # 1 heure de données

# Récupérer les données pour la station STRA
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)

# Fusionner les données si plusieurs fichiers
sta.merge(fill_value='interpolate')

# Calcul du spectrogramme
f, t, Sxx = signal.spectrogram(sta[0].data, fs=sta[0].stats.sampling_rate, nperseg=256, noverlap=192)

# Conversion de la densité spectrale en dB
Sxx_dB = 10 * np.log10(Sxx)

# Conversion de `t` en UTC pour l'affichage sur l'axe des x
start_time = UTCDateTime(ti)
time_in_utc = np.array([start_time + pd.to_timedelta(ti, unit='s') for ti in t], dtype='datetime64[s]')

# Création du spectrogramme avec plt.pcolormesh
plt.figure(figsize=(12, 6))
plt.pcolormesh(time_in_utc, f, Sxx_dB, shading='gouraud', cmap='viridis')

# Limiter la plage de fréquences
plt.ylim(0.03, 24)  # Plage souhaitée de 0.03 Hz à 24 Hz

# Ajouter des labels et un titre
plt.title(f"Spectrogramme de {sta[0].stats.station}")
plt.ylabel('Fréquence [Hz]')
plt.xlabel('Temps (UTC)')

# Ajouter la barre de couleur
plt.colorbar(label='Amplitude (dB)')

# Afficher le spectrogramme
plt.tight_layout()
plt.show()
