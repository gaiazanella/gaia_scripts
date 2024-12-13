import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client

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

# Création du spectrogramme
plt.figure(figsize=(12, 6))
Pxx, freqs, bins, im = plt.specgram(sta[0].data, NFFT=256, Fs=sta[0].stats.sampling_rate, noverlap=192, cmap='viridis')

# Limiter la plage de fréquences
plt.ylim(0.03, 24)  # Plage souhaitée de 0.03 Hz à 24 Hz

# Ajouter des labels et un titre
plt.title(f"Spectrogramme de {sta[0].stats.station}")
plt.ylabel('Fréquence [Hz]')

# Ajouter la barre de couleur
plt.colorbar(label='Amplitude (dB)')

# Calculer les étiquettes de temps en format UTC
time_utc = [ti + i / fs for i in range(len(sta[0].data))]

# Fonction pour ajuster les étiquettes en fonction de la vue actuelle
def update_xticks(event):
    xlim = plt.gca().get_xlim()
    start_idx = int(xlim[0] * fs)
    end_idx = int(xlim[1] * fs)
    
    # Ajuster les indices pour les étiquettes
    labels = [time_utc[i].strftime('%Y-%m-%d %H:%M:%S') for i in range(start_idx, end_idx, int((end_idx - start_idx) / 10))]
    plt.xticks(np.linspace(xlim[0], xlim[1], num=len(labels)), labels, rotation=45)

# Connecter la fonction au zoom
plt.gcf().canvas.mpl_connect('draw_event', update_xticks)

# Afficher le spectrogramme
plt.tight_layout()
plt.show()
