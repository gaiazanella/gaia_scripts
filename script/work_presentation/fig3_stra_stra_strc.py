##### copie de stre_a_strg_g_daily_vero_plot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Chemin vers le fichier CSV contenant les ratios
file_path = '/home/gaia/Documents/processing_1_sec/2020/rsam_ratio/ratio_rsam_stra_stre_strg_20200323.csv'

# Charger le fichier CSV dans un DataFrame
data_csv = pd.read_csv(file_path)

# Convertir la colonne 'time_UTC' en format datetime
data_csv['time_UTC'] = pd.to_datetime(data_csv['time_UTC'])

# Afficher les premières lignes pour vérifier le contenu
print("Contenu du fichier CSV des ratios :")
print(data_csv.head())

# Charger le fichier CSV contenant les données des pics (étoiles)
peaks_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv'
peaks_data = pd.read_csv(peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
peaks_data['Peak_Time_UTC'] = pd.to_datetime(peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics
print("Contenu du fichier CSV des pics :")
print(peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRG/STRA
strg_stra_peaks_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra_0.5/strg_stra_peaks_data_20200323.csv'
strg_stra_peaks_data = pd.read_csv(strg_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strg_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strg_stra_peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRG/STRA
print("Contenu du fichier CSV des pics STRG/STRA :")
print(strg_stra_peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRC/STRA
strc_stra_peaks_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strc_stra_0.5/strc_stra_peaks_data_20200323.csv'
strc_stra_peaks_data = pd.read_csv(strc_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strc_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strc_stra_peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRC/STRA
print("Contenu du fichier CSV des pics STRC/STRA :")
print(strc_stra_peaks_data.head())

# Configuration pour récupérer les données sismiques
db = '/mnt/bigmama3/miniseed'
stations = ['STRE', 'STRA', 'STRG', 'STRC']  # Ajouter STRC
network = '*'  # Accepter tous les réseaux
channel = '*HZ'  # Composante Z
fs = 50  # Fréquence d'échantillonnage cible

client = Client(db)

# Période d'intérêt
ti = UTCDateTime("2020-03-23T00:00:00.000")
tf = ti + 60 * 60 * 24  # Une journée complète

# Récupérer et prétraiter les données pour les quatre stations
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
    elif station == 'STRG':  # Filtrage pour STRG (8-15 Hz)
        data_sismique['STRG'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRC':  # Filtrage pour STRC (8-15 Hz)
        data_sismique['STRC'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)

    # Créer un axe temporel pour chaque station
    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[f'{station}_time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(len(st[0].data)) / fs, unit='s'))

# Calculer les valeurs min et max des 5 premiers signaux
y_min = min(np.min(data_sismique['STRA']), np.min(data_sismique['STRE']), np.min(data_sismique['STRG']), np.min(data_sismique['STRC']))
y_max = max(np.max(data_sismique['STRA']), np.max(data_sismique['STRE']), np.max(data_sismique['STRG']), np.max(data_sismique['STRC']))

# Créer une figure avec sept sous-graphiques (subplots) empilés, en partageant l'axe X
fig, ax = plt.subplots(7, 1, figsize=(12, 21), sharex=True)  # 7 sous-graphes

# Premier graphique : Données filtrées pour STRA (0.03-1 Hz)
ax[0].plot(data_sismique['STRA_time'], data_sismique['STRA'], color='red', label='STRA (0.03-1 Hz)')
ax[0].set_ylabel('RSAM (counts)')
ax[0].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
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

# Quatrième graphique : Données filtrées pour STRC (8-15 Hz) - avec couleur cyan
ax[3].plot(data_sismique['STRC_time'], data_sismique['STRC'], color='cyan', label='STRC (8-15 Hz)')
ax[3].set_ylabel('RSAM (counts)')
ax[3].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[3].legend(loc='upper right')
ax[3].grid(True)

# Cinquième graphique : Ratio STRE/STRA (E/A)
ax[4].plot(data_csv['time_UTC'], data_csv['Ratio_STRE_STRA'], color='orange', label='STRE/STRA')
ax[4].set_ylabel('Ratio')
ax[4].legend(loc='upper right')
ax[4].grid(True)

# Ajouter des étoiles basées sur les pics du fichier peaks_data.csv
ax[4].scatter(peaks_data['Peak_Time_UTC'], peaks_data['Ratio'], color='red', marker='*', label='Detection (E/A)')
ax[4].legend()

# Sixième graphique : Ratio STRG/STRA (G/A)
ax[5].plot(data_csv['time_UTC'], data_csv['Ratio_STRG_STRA'], color='green', label='STRG/STRA')
ax[5].set_ylabel('Ratio')
ax[5].legend(loc='upper right')
ax[5].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strg_stra_peaks_data.csv
ax[5].scatter(strg_stra_peaks_data['Peak_Time_UTC'], strg_stra_peaks_data['Ratio'], color='blue', marker='*', label='Detection (G/A)')
ax[5].legend(loc='upper right')

# Septième graphique : Ratio STRC/STRA (C/A)
ax[6].plot(data_csv['time_UTC'], data_csv['Ratio_STRC_STRA'], color='purple', label='STRC/STRA')
ax[6].set_ylabel('Ratio')
ax[6].legend(loc='upper right')
ax[6].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strc_stra_peaks_data.csv
ax[6].scatter(strc_stra_peaks_data['Peak_Time_UTC'], strc_stra_peaks_data['Ratio'], color='pink', marker='*', label='Detection (C/A)')
ax[6].legend(loc='upper right')

# Ajuster l'espacement entre les sous-graphiques
plt.tight_layout()

# Afficher les graphiques
plt.show()
