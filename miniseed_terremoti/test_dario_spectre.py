import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy import interpolate
from obspy import read
from scipy.signal import detrend

# Fonction pour le lissage logarithmique
def smooth_log(data, window_length):
    log_data = np.log(data)  # Appliquer le logarithme
    smoothed = np.convolve(log_data, np.ones(window_length) / window_length, mode='same')
    return np.exp(smoothed)  # Retourner les valeurs lissées en exponentielle

# Charger les données sismiques
stream_station = read("/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed")

# Detrend pour mettre le signal autour de zéro
stream_station.detrend("demean")
stream_station.detrend("linear")

print(stream_station)

# Paramètres
STZ = ['STR1','STR4','STRA', 'STRC', 'STRE', 'STRG']
sconv = [1, 1, 1, 1, 1, 1]  # Facteurs de conversion (ajuster selon les données)

# Récupérer le temps

tt = stream_station[0].times()
plt.figure()
for i in range(len(STZ)):
    plt.plot(tt, stream_station[i].data, label=f"Station {STZ[i]}")

plt.title('Composante Verticale - Toutes les Stations')
plt.xlabel('Temps')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.ion()  # Mode interactif pour zoom
plt.show()

# 2. Sélectionner l'intervalle temporel
a = plt.ginput(2)  # Sélectionner deux points avec la souris
a = sorted(a)  # Trier les points

#tt = stream_station[0].times()  # Temps de la première station, on suppose qu'il est identique pour toutes les stations

# Visualisation des données
#plt.figure()
#plt.plot(tt, stream_station[0].data)  # On prend la composante verticale pour la première station
#plt.grid(True)
#plt.title('Composante Verticale')
#plt.xlabel('Temps')
#plt.ylabel('Amplitude')
#plt.ion()  # Mode interactif pour zoom
#plt.show()

# 2. Sélectionner l'intervalle temporel
#a = plt.ginput(2)  # Sélectionner deux points avec la souris
#a = sorted(a)  # Trier les points

# Initialisation de la liste des spectres de puissance
PXX = []


# 3. Boucle pour chaque station
for i in range(len(STZ)):
    # Récupérer la trace de la station i (composante verticale)
    yy = stream_station[i].data
    
    # Définir l'intervalle de temps de l'utilisateur
    ii = np.where((tt > a[0][0]) & (tt < a[1][0]))[0]
    tt_cut = tt[ii]
    yy_cut = yy[ii] / sconv[i]  # Appliquer le facteur de conversion
    
    # Calcul du taux d'échantillonnage
    smp = np.round(1 / (tt_cut[1] - tt_cut[0]) * 86400)  # Taux d'échantillonnage en secondes
    
    # Calcul du spectre de puissance avec Welch
    f, pxx = welch(yy_cut - np.mean(yy_cut), fs=smp, nperseg=2**16)
    
    # Ajouter le spectre de puissance à la liste
    PXX.append(pxx)

# Convertir PXX en un tableau numpy 2D
PXX = np.array(PXX)

# 4. Choisir la station de référence
iref = 5  # Choisir la station de référence (index 7 en MATLAB correspond à 6 en Python)

# 5. Sélectionner l'intervalle de fréquence
ii_freq = np.where((f > 0.01) & (f < 24))[0]
a0 = smooth_log(PXX[iref, ii_freq], window_length=1)  # Appliquer un lissage logarithmique

# 6. Nouveau calcul pour toutes les stations
A = np.zeros(len(STZ))  # Moyenne des rapports spectraux
Am = np.zeros(len(STZ))  # Déviation standard des rapports spectraux
ratio = np.zeros_like(PXX)  # Matrice pour les rapports spectraux

for i in range(len(STZ)):
    # Calcul du rapport spectral
    ratio[:, i] = np.sqrt(smooth_log(PXX[i, ii_freq] / a0, window_length=1))
    
    # Calcul de la moyenne et de la déviation standard des rapports
    A[i] = np.mean(ratio[:, i])
    Am[i] = np.std(ratio[:, i])

