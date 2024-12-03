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

# Temps de départ et la durée des données
starttime = sta[0].stats.starttime
duration = sta[0].stats.npts / sta[0].stats.sampling_rate  # Durée des données en secondes

# Vecteur de temps pour l'axe des X (en UTC)
time_utc = [starttime + i / fs for i in range(len(sta[0].data))]

# Création du spectrogramme
plt.figure(figsize=(12, 6))
Pxx, freqs, bins, im = plt.specgram(sta[0].data, NFFT=128, Fs=sta[0].stats.sampling_rate, noverlap=64, cmap='viridis')

# Ajouter des labels et un titre
plt.title(f"Spectrogramme de {sta[0].stats.station}")
plt.xlabel('Temps (UTC)')
plt.ylabel('Fréquence [Hz]')

# Ajouter la barre de couleur
plt.colorbar(label='Amplitude (dB)')

# Ajouter l'axe des x avec des dates UTC
def update_xticks():
    # Récupérer les limites de l'axe des x
    xlim = plt.gca().get_xlim()
    
    # Mettre à jour les dates en fonction des limites de l'axe x
    start_idx = int(xlim[0] * fs)
    end_idx = int(xlim[1] * fs)
    
    # Créer des labels de temps sur l'axe x, en convertissant les indices en dates UTC
    labels = [(starttime + i / fs).strftime('%Y-%m-%d %H:%M:%S') for i in range(start_idx, end_idx, int((end_idx - start_idx) / 10))]
    
    # Mettre à jour les ticks de l'axe x
    plt.xticks(np.linspace(xlim[0], xlim[1], num=len(labels)), labels, rotation=45)

# Initialiser l'axe x avec des dates UTC
update_xticks()

# Connecter le zoom interactif à la mise à jour des ticks
plt.gcf().canvas.mpl_connect('draw_event', lambda event: update_xticks())

# Afficher le spectrogramme
plt.tight_layout()
plt.show()
