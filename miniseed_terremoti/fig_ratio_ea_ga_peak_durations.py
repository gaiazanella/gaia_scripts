##### copie de stre_a_strg_g_daily_vero_plot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Chemin vers le fichier CSV contenant les ratios
file_path = '/home/gaia/Documents/processing_10_sec/2020/rsam_ratio/ratio_rsam_stra_stre_strg_20200323.csv'

# Charger le fichier CSV dans un DataFrame
data_csv = pd.read_csv(file_path)

# Convertir la colonne 'time_UTC' en format datetime
data_csv['time_UTC'] = pd.to_datetime(data_csv['time_UTC'])

# Afficher les premières lignes pour vérifier le contenu
print("Contenu du fichier CSV des ratios :")
print(data_csv.head())

# Charger le fichier CSV contenant les données des pics (étoiles)
peaks_file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv'
peaks_data = pd.read_csv(peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
peaks_data['Peak_Time_UTC'] = pd.to_datetime(peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics
print("Contenu du fichier CSV des pics :")
print(peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRG/STRA
strg_stra_peaks_file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra/strg_stra_peaks_data_20200323.csv'
strg_stra_peaks_data = pd.read_csv(strg_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strg_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strg_stra_peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRG/STRA
print("Contenu du fichier CSV des pics STRG/STRA :")
print(strg_stra_peaks_data.head())

# Configuration pour récupérer les données sismiques
db = '/mnt/bigmama3/miniseed'
stations = ['STRE', 'STRA', 'STRG']  # Ajouter STRG
network = '*'  # Accepter tous les réseaux
channel = '*HZ'  # Composante Z
fs = 50  # Fréquence d'échantillonnage cible

client = Client(db)

# Période d'intérêt
ti = UTCDateTime("2020-03-23T00:00:00.000")
tf = ti + 60 * 60 * 24  # Une journée complète

# Récupérer et prétraiter les données pour les trois stations
data_sismique = {}
for station in stations:
    st = client.get_waveforms(network=network, station=station, location="", channel=channel, starttime=ti, endtime=tf)
    print(f"Données de la station sismique {station} récupérées :", st)
    st.merge(fill_value='interpolate')
    st.detrend("demean")
    st.detrend("linear")
    if station == 'STRE':
        # Filtrage pour STRE (8–15 Hz)
        data_sismique['STRE'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRA':
        # Filtrage pour STRA (0.03–1 Hz)
        data_sismique['STRA'] = bandpass(st[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
    elif station == 'STRG':  # Ajouter le traitement pour STRG
        # Filtrage pour STRG (8-15 Hz)
        data_sismique['STRG'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)

    # Créer un axe temporel pour chaque station
    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[f'{station}_time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(len(st[0].data)) / fs, unit='s'))

# Calculer les valeurs min et max des 3 premiers signaux
y_min = min(np.min(data_sismique['STRA']), np.min(data_sismique['STRE']), np.min(data_sismique['STRG']))
y_max = max(np.max(data_sismique['STRA']), np.max(data_sismique['STRE']), np.max(data_sismique['STRG']))

# Calculer les limites min et max des deux ratios
ratio_min = min(np.min(data_csv['Ratio_STRE_STRA']), np.min(data_csv['Ratio_STRG_STRA']))
ratio_max = max(np.max(data_csv['Ratio_STRE_STRA']), np.max(data_csv['Ratio_STRG_STRA']))

# Créer une figure avec cinq sous-graphiques (subplots) empilés, en partageant l'axe X
fig, ax = plt.subplots(5, 1, figsize=(12, 15), sharex=True)  # 5 sous-graphes

# Premier graphique : Données filtrées pour STRA (0.03-1 Hz)
ax[0].plot(data_sismique['STRA_time'], data_sismique['STRA'], color='red', label='STRA (0.03-1 Hz)')
ax[0].set_ylabel('RSAM (counts)')
#ax[0].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[0].legend(loc='upper right')
ax[0].grid(True)

# Deuxième graphique : Données filtrées pour STRE (8-15 Hz)
ax[1].plot(data_sismique['STRE_time'], data_sismique['STRE'], color='blue', label='STRE (8-15 Hz)')
ax[1].set_ylabel('RSAM (counts)')
ax[1].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[1].legend(loc='upper right')
ax[1].grid(True)

# Troisième graphique : Données filtrées pour STRG (8-15 Hz) - avec couleur magenta
ax[2].plot(data_sismique['STRG_time'], data_sismique['STRG'], color='magenta', label='STRG (8-15 Hz)')
ax[2].set_ylabel('RSAM (counts)')
ax[2].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[2].legend(loc='upper right')
ax[2].grid(True)

# Quatrième graphique : Ratio STRE/STRA (E/A)
ax[3].plot(data_csv['time_UTC'], data_csv['Ratio_STRE_STRA'], color='orange', label='STRE/STRA')
ax[3].set_ylabel('Ratio')
ax[3].set_ylim(ratio_min, ratio_max)  # Appliquer les mêmes limites pour l'axe y
ax[3].legend(loc='upper right')
ax[3].legend(loc='upper right')
ax[3].grid(True)

# Ajouter des étoiles basées sur les pics du fichier peaks_data.csv
ax[3].scatter(peaks_data['Peak_Time_UTC'], peaks_data['Ratio'], color='red', marker='*', label='Detection (E/A)')
ax[3].legend()

# Cinquième graphique : Ratio STRG/STRA (G/A)
ax[4].plot(data_csv['time_UTC'], data_csv['Ratio_STRG_STRA'], color='green', label='STRG/STRA')
ax[4].set_ylabel('Ratio')
#ax[4].set_ylim(ratio_min, ratio_max)  # Appliquer les mêmes limites pour l'axe y
ax[4].legend(loc='upper right')
ax[4].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strg_stra_peaks_data.csv
ax[4].scatter(strg_stra_peaks_data['Peak_Time_UTC'], strg_stra_peaks_data['Ratio'], color='blue', marker='*', label='Detection (G/A)')
ax[4].legend(loc='upper right')

# Ajuster l'espacement entre les sous-graphiques
plt.tight_layout()

# Afficher les graphiques
plt.show()
