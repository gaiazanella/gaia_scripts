from obspy.clients.filesystem.sds import Client
from obspy import UTCDateTime
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend  # Importation de scipy.signal
import numpy as np
from obspy.signal.util import smooth  # Importation de smooth depuis obspy.signal.util

# Initialiser le client pour le répertoire SDS
client = Client("/mnt/bigmama3")

# Heure de départ
t_eq = UTCDateTime("2025-02-07T15:19:30")
t_noise = UTCDateTime("2025-02-07T15:18:30")
dt = 30  # Durée d'enregistrement en secondes

# Stations et canaux à récupérer
stations = ['STRA', 'STRC', 'STRE', 'STRG']
channel = '*HZ'  # Le canal à récupérer (tous les canaux horizontaux)

# Dictionnaire pour attribuer des couleurs spécifiques à chaque station
colors = {
    'STRA': 'red',   # STRA en rouge
    'STRC': 'cyan',  # STRC en cyan
    'STRE': 'blue',  # STRE en bleu
    'STRG': 'magenta' # STRG en magenta
}

# Créer une figure pour l'affichage
plt.figure(figsize=(8, 5))

# Récupérer les données pour STRA et calculer la densité spectrale de puissance pour "EQ"
sz_stra_eq = client.get_waveforms(network="*", station="STRA", location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
data_stra_eq = sz_stra_eq[0].data
data_stra_eq_detrended = detrend(data_stra_eq)
data_stra_eq_demeaned = data_stra_eq_detrended - np.mean(data_stra_eq_detrended)
f_stra_eq, Pxx_stra_eq = welch(data_stra_eq_demeaned * 1E-6 / 800, fs=100, nperseg=len(data_stra_eq))

# Récupérer les données pour STRA et calculer la densité spectrale de puissance pour "Noise"
sz_stra_noise = client.get_waveforms(network="*", station="STRA", location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)
data_stra_noise = sz_stra_noise[0].data
data_stra_noise_detrended = detrend(data_stra_noise)
data_stra_noise_demeaned = data_stra_noise_detrended - np.mean(data_stra_noise_detrended)
f_stra_noise, Pxx_stra_noise = welch(data_stra_noise_demeaned * 1E-6 / 800, fs=100, nperseg=len(data_stra_noise))

# Parcourir les stations et récupérer les formes d'onde pour les deux périodes (EQ et Noise)
for station in stations:
    if station == 'STRA':  # Skip STRA for the spectral ratio
        continue
    
    # Récupérer les données pour la période "EQ"
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    data_eq = sz_eq[0].data
    data_eq_detrended = detrend(data_eq)
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 800, fs=100, nperseg=len(data_eq))

    # Récupérer les données pour la période "Noise"
    sz_noise = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)
    data_noise = sz_noise[0].data
    data_noise_detrended = detrend(data_noise)
    data_noise_demeaned = data_noise_detrended - np.mean(data_noise_detrended)
    f_noise, Pxx_noise = welch(data_noise_demeaned * 1E-6 / 800, fs=100, nperseg=len(data_noise))

    # Calculer le rapport spectral pour "EQ" (station / STRA)
    Pxx_eq_ratio = Pxx_eq / Pxx_stra_eq
    # Calculer le rapport spectral pour "Noise" (station / STRA)
    Pxx_noise_ratio = Pxx_noise / Pxx_stra_noise

    # Afficher le rapport spectral en fonction de la fréquence pour "EQ"
    plt.loglog(f_eq, smooth(Pxx_eq_ratio, 100), label=f"{station} - EQ / STRA", color=colors[station], linestyle='-', alpha=0.7)

    # Afficher le rapport spectral en fonction de la fréquence pour "Noise"
    plt.loglog(f_noise, smooth(Pxx_noise_ratio, 100), label=f"{station} - Noise / STRA", color=colors[station], linestyle='--', alpha=0.7)

# Configuration de la figure
plt.xlabel("Frequency (Hz)")
plt.ylabel("Spectral Ratio")
plt.title("Spectral Ratio (Station / STRA) for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()
