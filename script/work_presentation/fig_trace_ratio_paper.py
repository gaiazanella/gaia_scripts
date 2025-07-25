##### copie de stre_a_strg_g_daily_vero_plot
#### avant pour présentation 20200323
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client
import matplotlib.dates as mdates

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

# Configuration pour récupérer les données sismiques
db = '/mnt/bigmama3'
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

# Ajouter filtrage STRA (8–15 Hz) en plus de STRA (0.03–1 Hz)
st_stra_high = client.get_waveforms(network=network, station='STRA', location="", channel=channel, starttime=ti, endtime=tf)
st_stra_high.merge(fill_value='interpolate')
st_stra_high.detrend("demean")
st_stra_high.detrend("linear")
data_sismique['STRA_8_15'] = bandpass(st_stra_high[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
starttime_high = UTCDateTime(st_stra_high[0].stats.starttime).datetime
data_sismique['STRA_8_15_time'] = pd.to_datetime(starttime_high + pd.to_timedelta(np.arange(len(st_stra_high[0].data)) / fs, unit='s'))

# Conversion de counts à m/s
sconv = 2.4390e8  # facteur de conversion spécifique à l'instrument
for key in ['STRA', 'STRE', 'STRG', 'STRA_8_15']:
    if key in data_sismique:
        data_sismique[key] = data_sismique[key] / sconv


# Calculer les valeurs min et max des 3 premiers signaux
#y_min = min(np.min(data_sismique['STRA']), np.min(data_sismique['STRE']), np.min(data_sismique['STRG']))
#y_max = max(np.max(data_sismique['STRA']), np.max(data_sismique['STRE']), np.max(data_sismique['STRG']))

y_min=-4e-5
y_max=4e-5

# Calculer les limites min et max des deux ratios
ratio_min = min(np.min(data_csv['Ratio_STRE_STRA']), np.min(data_csv['Ratio_STRG_STRA']))
ratio_max = max(np.max(data_csv['Ratio_STRE_STRA']), np.max(data_csv['Ratio_STRG_STRA']))

# Créer une figure avec quatre sous-graphiques
fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

# 1er graphique : STRA (0.03–1 Hz)
ax[0].plot(data_sismique['STRA_time'], data_sismique['STRA'], color='red', label='STRA (0.03–1 Hz)')
ax[0].set_ylabel('Seismic record (m/s)')
ax[0].legend(loc='upper right')
ax[0].grid(True)

# 2e graphique : STRA (8–15 Hz)
ax[1].plot(data_sismique['STRA_8_15_time'], data_sismique['STRA_8_15'], color='red', label='STRA (8–15 Hz)')
ax[1].set_ylabel('Seismic record (m/s)')
ax[1].set_ylim(y_min, y_max)
ax[1].legend(loc='upper right')
ax[1].grid(True)

# 3e graphique : STRE (8–15 Hz)
ax[2].plot(data_sismique['STRE_time'], data_sismique['STRE'], color='blue', label='STRE (8–15 Hz)')
ax[2].set_ylabel('Seismic record (m/s)')
ax[2].set_ylim(y_min, y_max)  # même échelle
ax[2].legend(loc='upper right')
ax[2].grid(True)

# 4e graphique : Ratio STRE/STRA avec étoiles
ax[3].plot(data_csv['time_UTC'], data_csv['Ratio_STRE_STRA'], color='orange')
ax[3].set_ylabel('Amplitude Ratio')
ax[3].set_ylim(ratio_min, ratio_max)
ax[3].scatter(peaks_data['Peak_Time_UTC'], peaks_data['Ratio'], color='red', marker='*', label='Landslide detection')
ax[3].legend(loc='upper right')
ax[3].grid(True)

# Pour un zoom, ticks majeurs toutes les 5 minutes
ax[3].xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
ax[3].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Optionnel : ticks mineurs toutes les minutes pour plus de repères
ax[3].xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))

plt.setp(ax[3].xaxis.get_majorticklabels(), rotation=45, ha='right')


# Ajuster l’espacement
plt.tight_layout()

# Afficher
plt.show()
