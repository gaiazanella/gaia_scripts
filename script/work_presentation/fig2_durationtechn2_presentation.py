
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-03-23T02:52:00.000")
tf = ti + (60 * 60 * 24 * 1)  # 1 jour de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
st2 = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)

# Fusionner les données (interpolation)
st1.merge(fill_value='interpolate')
st2.merge(fill_value='interpolate')

# Detrend les signaux
st1.detrend("demean")
st1.detrend("linear")
st2.detrend("demean")
st2.detrend("linear")

# Appliquer les filtres bandpass sur les données
data1_full = bandpass(st1[0].data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data1_low = bandpass(st1[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

data2_full = bandpass(st2[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
data2_low = bandpass(st2[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime

time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1_full) / fs, 1 / fs), unit='s'))
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2_full) / fs, 1 / fs), unit='s'))

# Lire le fichier CSV contenant les événements
csv_file = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv' ## 1SEC
#csv_file = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv' ## 10SEC
df_csv = pd.read_csv(csv_file)

# Convertir les colonnes en format datetime
df_csv['Peak_Time_UTC'] = pd.to_datetime(df_csv['Peak_Time_UTC'])
df_csv['Initial_Peak_Time_w'] = pd.to_datetime(df_csv['Initial_Peak_Time_w'])
df_csv['Final_Peak_Time_w'] = pd.to_datetime(df_csv['Final_Peak_Time_w'])

# Charger les fichiers CSV pour RSAM (STRA et STRE)
rsam_stra_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRA_20200323.csv' #1SEC
rsam_stre_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRE_20200323.csv' #1SEC
#rsam_stra_file = '/home/gaia/Documents/processing_10_sec/2020/rsam/rsam_STRA_20200323.csv'
#rsam_stre_file = '/home/gaia/Documents/processing_10_sec/2020/rsam/rsam_STRE_20200323.csv'

rsam_stra = pd.read_csv(rsam_stra_file)
rsam_stre = pd.read_csv(rsam_stre_file)

# Convertir 'time_UTC' en datetime
rsam_stra['time_UTC'] = pd.to_datetime(rsam_stra['time_UTC'])
rsam_stre['time_UTC'] = pd.to_datetime(rsam_stre['time_UTC'])

# Calculer le rapport entre les RSAM de STRE et STRA (STRE / STRA)
rsam_ratio = rsam_stre['RSAM_env_smooth_8-15Hz'] / rsam_stra['RSAM_env_smooth_8-15Hz']

# Création de la figure avec 4 subplots
fig, axs = plt.subplots(4, 1, figsize=(12, 22), sharex=True)

# Subplot 1 : Trace filtrée 0.03-24 Hz
#axs[0].plot(time1, data1_full, color='red')
axs[0].plot(time2, data2_full, color='blue', label='STRE')
axs[0].set_ylabel('RSAM (counts) (8-15 Hz)')
axs[0].grid(True)

# Subplot 2 : Trace filtrée 0.03-1 Hz
axs[1].plot(time1, data1_low, color='red', label='STRA ')
#axs[1].plot(time2, data2_low, color='blue', label='STRE ')
axs[1].set_ylabel('RSAM (counts) (0.03-1 Hz)')
axs[1].grid(True)

# Subplot 3 : RSAM de chaque station (STRA et STRE)
axs[2].plot(rsam_stra['time_UTC'], rsam_stra['RSAM_env_smooth_8-15Hz'], color='red', label='STRA')
axs[2].plot(rsam_stre['time_UTC'], rsam_stre['RSAM_env_smooth_8-15Hz'], color='blue', label='STRE')
axs[2].set_ylabel('RSAM post processing (8-15 Hz)')
axs[2].legend()
axs[2].grid(True)

# Subplot 4 : Rapport entre les RSAM de STRE et STRA
axs[3].plot(rsam_stra['time_UTC'], rsam_ratio, color='orange')
axs[3].set_ylabel('RSAM(STRE) / RSAM(STRA)')
axs[3].grid(True)

# Ajouter des lignes verticales pour les 3 colonnes spécifiques (Peak_Time_UTC, Initial_Peak_Time_w, Final_Peak_Time_w)
event_colors = {
    'Peak_Time_UTC': 'green',  # Vert pour Peak_Time_UTC
    'Initial_Peak_Time_w': 'magenta',  # Bleu pour Initial_Peak_Time_w
    'Final_Peak_Time_w': 'purple',  # Rouge pour Final_Peak_Time_w
}

# Dictionnaire pour stocker les handles de légende
legend_handles = {}

# Ajouter des lignes verticales dans tous les subplots pour chaque colonne
for col, color in event_colors.items():
    filtered_events = df_csv[col].dropna()  # Eliminer les NaN

    for peak_time in filtered_events:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--', label=col)
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[2].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[3].axvline(x=peak_time_dt, color=color, linestyle='--')

        if time2.min() <= peak_time_dt <= time2.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--', label=col)
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[2].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[3].axvline(x=peak_time_dt, color=color, linestyle='--')

# Ajouter une légende et une étiquette d'axe
axs[3].set_xlabel('Time (UTC)')
fig.tight_layout()

# Afficher la légende avec uniquement les lignes verticales uniques
lines, labels = axs[0].get_legend_handles_labels()
unique_lines_labels = []
for line, label in zip(lines, labels):
    if label not in unique_lines_labels:
        unique_lines_labels.append(label)
        legend_handles[label] = line  # Ajouter le handle pour ce label dans le dictionnaire

# Afficher la légende avec les couleurs correctes
axs[0].legend(legend_handles.values(), legend_handles.keys(), loc='upper right')

# Affichage
plt.show()


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-03-23T02:52:00.000")
tf = ti + (60 * 60 * 24 * 1)  # 1 jour de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
st2 = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)

# Fusionner les données (interpolation)
st1.merge(fill_value='interpolate')
st2.merge(fill_value='interpolate')

# Detrend les signaux
st1.detrend("demean")
st1.detrend("linear")
st2.detrend("demean")
st2.detrend("linear")

# Appliquer les filtres bandpass sur les données
data1_full = bandpass(st1[0].data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data1_low = bandpass(st1[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

data2_full = bandpass(st2[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
data2_low = bandpass(st2[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime

time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1_full) / fs, 1 / fs), unit='s'))
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2_full) / fs, 1 / fs), unit='s'))

# Lire le fichier CSV contenant les événements
csv_file = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv' ##1SEC
#csv_file = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra/peaks_data_20200323.csv'
df_csv = pd.read_csv(csv_file)

# Convertir les colonnes en format datetime
df_csv['Peak_Time_UTC'] = pd.to_datetime(df_csv['Peak_Time_UTC'])
df_csv['Initial_Peak_Time'] = pd.to_datetime(df_csv['Initial_Peak_Time'])
df_csv['Final_Peak_Time'] = pd.to_datetime(df_csv['Final_Peak_Time'])

# Charger les fichiers CSV pour RSAM (STRA et STRE)
rsam_stra_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRA_20200323.csv' ##1SEC
rsam_stre_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRE_20200323.csv' ##1SEC
#rsam_stra_file = '/home/gaia/Documents/processing_10_sec/2020/rsam/rsam_STRA_20200323.csv'
#rsam_stre_file = '/home/gaia/Documents/processing_10_sec/2020/rsam/rsam_STRE_20200323.csv'

rsam_stra = pd.read_csv(rsam_stra_file)
rsam_stre = pd.read_csv(rsam_stre_file)

# Convertir 'time_UTC' en datetime
rsam_stra['time_UTC'] = pd.to_datetime(rsam_stra['time_UTC'])
rsam_stre['time_UTC'] = pd.to_datetime(rsam_stre['time_UTC'])

# Calculer le rapport entre les RSAM de STRE et STRA (STRE / STRA)
rsam_ratio = rsam_stre['RSAM_env_smooth_8-15Hz'] / rsam_stra['RSAM_env_smooth_8-15Hz']

# Création de la figure avec 4 subplots
fig, axs = plt.subplots(4, 1, figsize=(12, 22), sharex=True)

# Subplot 1 : Trace filtrée 0.03-24 Hz
#axs[0].plot(time1, data1_full, color='red')
axs[0].plot(time2, data2_full, color='blue', label='STRE')
axs[0].set_ylabel('RSAM (counts) (8-15 Hz)')
axs[0].grid(True)

# Subplot 2 : Trace filtrée 0.03-1 Hz
axs[1].plot(time1, data1_low, color='red', label='STRA ')
#axs[1].plot(time2, data2_low, color='blue', label='STRE ')
axs[1].set_ylabel('RSAM (counts) (0.03-1 Hz)')
axs[1].grid(True)

# Subplot 3 : RSAM de chaque station (STRA et STRE)
axs[2].plot(rsam_stra['time_UTC'], rsam_stra['RSAM_env_smooth_8-15Hz'], color='red', label='STRA')
axs[2].plot(rsam_stre['time_UTC'], rsam_stre['RSAM_env_smooth_8-15Hz'], color='blue', label='STRE')
axs[2].set_ylabel('RSAM post processing (8-15 Hz)')
axs[2].legend()
axs[2].grid(True)

# Subplot 4 : Rapport entre les RSAM de STRE et STRA
axs[3].plot(rsam_stra['time_UTC'], rsam_ratio, color='orange')
axs[3].set_ylabel('RSAM(STRE) / RSAM(STRA)')
axs[3].grid(True)

# Ajouter des lignes verticales pour les 3 colonnes spécifiques (Peak_Time_UTC, Initial_Peak_Time_w, Final_Peak_Time_w)
event_colors = {
    'Peak_Time_UTC': 'green',  # Vert pour Peak_Time_UTC
    'Initial_Peak_Time': 'magenta',  # Bleu pour Initial_Peak_Time_w
    'Final_Peak_Time': 'purple',  # Rouge pour Final_Peak_Time_w
}

# Dictionnaire pour stocker les handles de légende
legend_handles = {}

# Ajouter des lignes verticales dans tous les subplots pour chaque colonne
for col, color in event_colors.items():
    filtered_events = df_csv[col].dropna()  # Eliminer les NaN

    for peak_time in filtered_events:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--', label=col)
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[2].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[3].axvline(x=peak_time_dt, color=color, linestyle='--')

        if time2.min() <= peak_time_dt <= time2.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--', label=col)
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[2].axvline(x=peak_time_dt, color=color, linestyle='--')
            axs[3].axvline(x=peak_time_dt, color=color, linestyle='--')

# Ajouter une légende et une étiquette d'axe
axs[3].set_xlabel('Time (UTC)')
fig.tight_layout()

# Afficher la légende avec uniquement les lignes verticales uniques
lines, labels = axs[0].get_legend_handles_labels()
unique_lines_labels = []
for line, label in zip(lines, labels):
    if label not in unique_lines_labels:
        unique_lines_labels.append(label)
        legend_handles[label] = line  # Ajouter le handle pour ce label dans le dictionnaire

# Afficher la légende avec les couleurs correctes
axs[0].legend(legend_handles.values(), legend_handles.keys(), loc='upper right')

# Affichage
plt.show()
