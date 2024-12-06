import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Chemin vers le fichier CSV contenant les ratios
file_path = '/home/gaia/Documents/processing_1_sec/2020/rsam_ratio/ratio_rsam_stra_stre_strg_20200320.csv'

# Charger le fichier CSV dans un DataFrame
data_csv = pd.read_csv(file_path)

# Convertir la colonne 'time_UTC' en format datetime
data_csv['time_UTC'] = pd.to_datetime(data_csv['time_UTC'])

# Afficher les premières lignes pour vérifier le contenu
print("Contenu du fichier CSV des ratios :")
print(data_csv.head())

# Charger le fichier CSV contenant les données des pics (étoiles)
peaks_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/peaks_data_20200320.csv'
peaks_data = pd.read_csv(peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
peaks_data['Peak_Time_UTC'] = pd.to_datetime(peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics
print("Contenu du fichier CSV des pics :")
print(peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRG/STRA
strg_stra_peaks_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra/strg_stra_peaks_data_20200320.csv'
strg_stra_peaks_data = pd.read_csv(strg_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strg_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strg_stra_peaks_data['Peak_Time_UTC'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRG/STRA
print("Contenu du fichier CSV des pics STRG/STRA :")
print(strg_stra_peaks_data.head())

# Configuration pour récupérer les données sismiques
db = '/mnt/bigmama3/miniseed'
stations = ['STRE', 'STRA']  # Stations à récupérer
network = '*'  # Accepter tous les réseaux
channel = '*HZ'  # Composante Z
fs = 50  # Fréquence d'échantillonnage cible

client = Client(db)

# Période d'intérêt
ti = UTCDateTime("2020-03-20T00:00:00.000")
tf = ti + 60 * 60 * 24  # Une journée complète

# Récupérer et prétraiter les données pour les deux stations
data_sismique = {}
for station in stations:
    st = client.get_waveforms(network=network, station=station, location="", channel=channel, starttime=ti, endtime=tf)
    print(f"Données de la station sismique {station} récupérées :", st)
    st.merge(fill_value='interpolate')
    st.detrend("demean")
    st.detrend("linear")
    if station == 'STRE':
        # Filtrage pour STRE (0.03–24 Hz)
        data_sismique['STRE'] = bandpass(st[0].data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
    elif station == 'STRA':
        # Filtrage pour STRA (0.03–1 Hz)
        data_sismique['STRA'] = bandpass(st[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

    # Créer un axe temporel pour chaque station
    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[f'{station}_time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(len(st[0].data)) / fs, unit='s'))

# Créer une figure avec quatre sous-graphiques (subplots) empilés, en partageant l'axe X
fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)  # 4 sous-graphes

# Premier graphique : Ratio_STRE_STRA
ax[0].plot(data_csv['time_UTC'], data_csv['Ratio_STRE_STRA'], color='orange', label='STRE/STRA')
#ax[0].set_title('Ratio STRE/STRA')
ax[0].set_ylabel('Ratio')
ax[0].legend(loc='upper right')
ax[0].grid(True)

# Ajouter des étoiles basées sur les pics du fichier peaks_data.csv
ax[0].scatter(peaks_data['Peak_Time_UTC'], peaks_data['Ratio'], color='red', marker='*', label='Detection (E/A)')
ax[0].legend()

# Deuxième graphique : Ratio_STRG_STRA
ax[1].plot(data_csv['time_UTC'], data_csv['Ratio_STRG_STRA'], color='green', label='STRG/STRA')
#ax[1].set_title('Ratio STRG/STRA')
ax[1].set_ylabel('Ratio')
ax[1].legend(loc='upper right')
ax[1].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strg_stra_peaks_data.csv
ax[1].scatter(strg_stra_peaks_data['Peak_Time_UTC'], strg_stra_peaks_data['Ratio'], color='blue', marker='*', label='Detection (G/A)')
ax[1].legend(loc='upper right')

# Troisième graphique : Données sismiques filtrées pour STRE
ax[2].plot(data_sismique['STRE_time'], data_sismique['STRE'], color='blue', label='STRE (0.03-24 Hz)')
#ax[2].set_title('Données filtrées pour STRE (0.03-24 Hz)')
ax[2].set_ylabel('RSAM (counts)')
ax[2].legend(loc='upper right')
ax[2].grid(True)

# Quatrième graphique : Données sismiques filtrées pour STRA
ax[3].plot(data_sismique['STRA_time'], data_sismique['STRA'], color='red', label='STRA (0.03-1 Hz)')
#ax[3].set_title('Données filtrées pour STRA (0.03-1 Hz)')
ax[3].set_xlabel('Time (UTC)')
ax[3].set_ylabel('RSAM (counts)')
ax[3].legend(loc='upper right')
ax[3].grid(True)

# Ajuster l'espacement entre les sous-graphiques
plt.tight_layout()

# Afficher les graphiques
plt.show()
