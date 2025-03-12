from obspy.clients.filesystem.sds import Client
from obspy import UTCDateTime
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend  # Importation correcte de detrend
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

# Parcourir les stations et récupérer les formes d'onde pour les deux périodes
for station in stations:
    # Récupérer les données pour la période "EQ"
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    # Récupérer les données pour la période "Noise"
    sz_noise = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)

    # Récupérer les données pour "EQ"
    data_eq = sz_eq[0].data
    # Appliquer detrend et demean sur les données "EQ"
    data_eq_detrended = detrend(data_eq)  # Enlève la tendance linéaire
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)  # Retire la moyenne

    # Récupérer les données pour "Noise"
    data_noise = sz_noise[0].data
    # Appliquer detrend et demean sur les données "Noise"
    data_noise_detrended = detrend(data_noise)  # Enlève la tendance linéaire
    data_noise_demeaned = data_noise_detrended - np.mean(data_noise_detrended)  # Retire la moyenne

    # Fréquence d'échantillonnage
    fs = 100
    nperseg = len(data_eq)
    noverlap = 128
    
    # Calculer la densité spectrale de puissance pour "EQ" (données traitées)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Calculer la densité spectrale de puissance pour "Noise" (données traitées)
    f_noise, Pxx_noise = welch(data_noise_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Afficher l'amplitude en fonction de la fréquence sur une échelle logarithmique pour "EQ"
    plt.loglog(f_eq, smooth(Pxx_eq, 1), label=f"{station} - EQ", color=colors[station], linestyle='-', alpha=0.7)

    # Afficher l'amplitude en fonction de la fréquence sur une échelle logarithmique pour "Noise"
    plt.loglog(f_noise, smooth(Pxx_noise, 1), label=f"{station} - Noise", color=colors[station], linestyle='--', alpha=0.7)

# Configuration de la figure
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Amplitude Spectrum using Welch's Method for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()


# Créer la deuxième figure pour les fréquences entre 8 et 15 Hz
plt.figure(figsize=(8, 5))

# Filtrer et afficher les spectres dans la plage de fréquence [8, 15] Hz
for station in stations:
    # Récupérer les données pour la période "EQ"
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    # Récupérer les données pour la période "Noise"
    sz_noise = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)

    # Récupérer les données pour "EQ"
    data_eq = sz_eq[0].data
    # Appliquer detrend et demean sur les données "EQ"
    data_eq_detrended = detrend(data_eq)  # Enlève la tendance linéaire
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)  # Retire la moyenne

    # Récupérer les données pour "Noise"
    data_noise = sz_noise[0].data
    # Appliquer detrend et demean sur les données "Noise"
    data_noise_detrended = detrend(data_noise)  # Enlève la tendance linéaire
    data_noise_demeaned = data_noise_detrended - np.mean(data_noise_detrended)  # Retire la moyenne

    # Fréquence d'échantillonnage
    fs = 100
    nperseg = len(data_eq)
    noverlap = 128

    # Calculer la densité spectrale de puissance pour "EQ" (données traitées)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)
##IT 3.2E-6/800
##IV 1E-6/1200

    # Calculer la densité spectrale de puissance pour "Noise" (données traitées)
    f_noise, Pxx_noise = welch(data_noise_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Filtrer les fréquences et la densité spectrale de puissance pour la plage [8, 15] Hz
    idx_eq = (f_eq >= 8) & (f_eq <= 15)
    idx_noise = (f_noise >= 8) & (f_noise <= 15)

    # Afficher l'amplitude pour les fréquences entre 8 et 15 Hz pour "EQ"
    plt.loglog(f_eq[idx_eq], smooth(Pxx_eq[idx_eq], 1), label=f"{station} - EQ", color=colors[station], linestyle='-', alpha=0.7)

    # Afficher l'amplitude pour les fréquences entre 8 et 15 Hz pour "Noise"
    plt.loglog(f_noise[idx_noise], smooth(Pxx_noise[idx_noise], 1), label=f"{station} - Noise", color=colors[station], linestyle='--', alpha=0.7)

# Configuration de la deuxième figure
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Amplitude Spectrum (8-15 Hz) using Welch's Method for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()
