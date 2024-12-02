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
ti = UTCDateTime("2020-10-22T00:00:00.000")
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

# Appliquer un filtre bandpass sur les données
data1 = st1[0].data
data2 = st2[0].data
data1 = bandpass(data1, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data2 = bandpass(data2, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime
time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1) / fs, 1 / fs), unit='s'))
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2) / fs, 1 / fs), unit='s'))

# Lire le fichier CSV contenant les événements
csv_file = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed/peaks_data_20201022.csv'
df_csv = pd.read_csv(csv_file)

# Convertir les valeurs des colonnes en format datetime
df_csv['Peak_Time_UTC'] = pd.to_datetime(df_csv['Peak_Time_UTC'])
df_csv['Initial_Peak_Time'] = pd.to_datetime(df_csv['Initial_Peak_Time'])
df_csv['Final_Peak_Time'] = pd.to_datetime(df_csv['Final_Peak_Time'])
df_csv['Initial_Peak_Time_w'] = pd.to_datetime(df_csv['Initial_Peak_Time_w'])
df_csv['Final_Peak_Time_w'] = pd.to_datetime(df_csv['Final_Peak_Time_w'])

# Filtrer les événements selon les critères
if 'RSAM_E' in df_csv.columns and 'Ratio' in df_csv.columns:
    filtered_events = df_csv[(df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5)]
    non_filtered_events = df_csv[~((df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5))]
else:
    print("Les colonnes 'RSAM_E' et 'Ratio' n'existent pas dans le DataFrame.")
    filtered_events = pd.DataFrame()
    non_filtered_events = df_csv

# Création des subplots (3 sous-graphiques)
fig, axs = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

# Couleurs associées
event_colors = {
    'Stra': 'r',  # Rouge pour STRA
    'Stre': 'b',  # Bleu pour STRE
    'Filtered': 'lime',  # Vert clair pour événements filtrés
    'Unfiltered': 'darkgreen',  # Vert foncé pour non filtrés
    'Initial_Peak_Time': 'purple',
    'Final_Peak_Time': 'orange',
    'Initial_Peak_Time_w': 'cyan',
    'Final_Peak_Time_w': 'magenta'
}

# 1er subplot pour STRA
axs[0].plot(time1, data1, color=event_colors['Stra'], label='STRA')
axs[0].set_ylabel('RSAM (counts)')
axs[0].grid(True)

# 2ème subplot pour STRE
axs[1].plot(time2, data2, color=event_colors['Stre'], label='STRE')
axs[1].set_ylabel('RSAM (counts)')
axs[1].grid(True)

# 3ème subplot pour les deux stations
axs[2].plot(time1, data1, color=event_colors['Stra'], label='STRA')
axs[2].plot(time2, data2, color=event_colors['Stre'], label='STRE')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('RSAM (counts)')
axs[2].legend()
axs[2].grid(True)

# Tracer tous les événements avec distinction des types
for event_set, color in [(filtered_events, event_colors['Filtered']), 
                         (non_filtered_events, event_colors['Unfiltered'])]:
    for peak_time in event_set['Peak_Time_UTC']:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--')
        if time2.min() <= peak_time_dt <= time2.max():
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')

# Tracer toutes les colonnes temporelles pour tous les événements
for time_col in ['Initial_Peak_Time', 'Final_Peak_Time', 'Initial_Peak_Time_w', 'Final_Peak_Time_w']:
    for peak_time in df_csv[time_col]:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=event_colors[time_col], linestyle='-')
        if time2.min() <= peak_time_dt <= time2.max():
            axs[1].axvline(x=peak_time_dt, color=event_colors[time_col], linestyle='-')

# Légende
legend_elements = [
    plt.Line2D([0], [0], color=event_colors['Stra'], lw=2, label='STRA'),
    plt.Line2D([0], [0], color=event_colors['Stre'], lw=2, label='STRE'),
    plt.Line2D([0], [0], color=event_colors['Filtered'], lw=2, linestyle='--', label='Glissement de terrain (Filtré)'),
    plt.Line2D([0], [0], color=event_colors['Unfiltered'], lw=2, linestyle='--', label='Glissement de terrain (Non filtré)'),
    plt.Line2D([0], [0], color=event_colors['Initial_Peak_Time'], lw=2, label='Initial_Peak_Time'),
    plt.Line2D([0], [0], color=event_colors['Final_Peak_Time'], lw=2, label='Final_Peak_Time'),
    plt.Line2D([0], [0], color=event_colors['Initial_Peak_Time_w'], lw=2, label='Initial_Peak_Time_w'),
    plt.Line2D([0], [0], color=event_colors['Final_Peak_Time_w'], lw=2, label='Final_Peak_Time_w'),
]

axs[0].legend(handles=legend_elements, loc='upper right')
plt.tight_layout()
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
ti = UTCDateTime("2020-10-22T00:00:00.000")
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

# Appliquer un filtre bandpass sur les données
data1 = st1[0].data
data2 = st2[0].data
data1 = bandpass(data1, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
data2 = bandpass(data2, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

# Convertir les temps en datetime
starttime1 = UTCDateTime(st1[0].stats.starttime).datetime
starttime2 = UTCDateTime(st2[0].stats.starttime).datetime
time1 = pd.to_datetime(starttime1 + pd.to_timedelta(np.arange(0, len(data1) / fs, 1 / fs), unit='s'))
time2 = pd.to_datetime(starttime2 + pd.to_timedelta(np.arange(0, len(data2) / fs, 1 / fs), unit='s'))

# Lire le fichier CSV contenant les événements
csv_file = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed/peaks_data_20201022.csv'
df_csv = pd.read_csv(csv_file)

# Convertir les valeurs des colonnes en format datetime
df_csv['Peak_Time_UTC'] = pd.to_datetime(df_csv['Peak_Time_UTC'])
df_csv['Initial_Peak_Time'] = pd.to_datetime(df_csv['Initial_Peak_Time'])
df_csv['Final_Peak_Time'] = pd.to_datetime(df_csv['Final_Peak_Time'])
df_csv['Initial_Peak_Time_w'] = pd.to_datetime(df_csv['Initial_Peak_Time_w'])
df_csv['Final_Peak_Time_w'] = pd.to_datetime(df_csv['Final_Peak_Time_w'])

# Filtrer les événements selon les critères
if 'RSAM_E' in df_csv.columns and 'Ratio' in df_csv.columns:
    filtered_events = df_csv[(df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5)]
    non_filtered_events = df_csv[~((df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5))]
else:
    print("Les colonnes 'RSAM_E' et 'Ratio' n'existent pas dans le DataFrame.")
    filtered_events = pd.DataFrame()
    non_filtered_events = df_csv

# Création des subplots (3 sous-graphiques)
fig, axs = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

# Couleurs associées
event_colors = {
    'Stra': 'r',  # Rouge pour STRA
    'Stre': 'b',  # Bleu pour STRE
    'Filtered': 'lime',  # Vert clair pour événements filtrés
    'Unfiltered': 'darkgreen',  # Vert foncé pour non filtrés
    'Initial_Peak_Time': 'purple',
    'Final_Peak_Time': 'orange',
    'Initial_Peak_Time_w': 'cyan',
    'Final_Peak_Time_w': 'magenta'
}

# 1er subplot pour STRA
axs[0].plot(time1, data1, color=event_colors['Stra'], label='STRA')
axs[0].set_ylabel('RSAM (counts)')
axs[0].grid(True)

# 2ème subplot pour STRE
axs[1].plot(time2, data2, color=event_colors['Stre'], label='STRE')
axs[1].set_ylabel('RSAM (counts)')
axs[1].grid(True)

# 3ème subplot pour les deux stations
axs[2].plot(time1, data1, color=event_colors['Stra'], label='STRA')
axs[2].plot(time2, data2, color=event_colors['Stre'], label='STRE')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('RSAM (counts)')
axs[2].legend()
axs[2].grid(True)

# Tracer tous les événements avec distinction des types
for event_set, color in [(filtered_events, event_colors['Filtered']), 
                         (non_filtered_events, event_colors['Unfiltered'])]:
    for peak_time in event_set['Peak_Time_UTC']:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=color, linestyle='--')
        if time2.min() <= peak_time_dt <= time2.max():
            axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')

# Tracer toutes les colonnes temporelles pour tous les événements
for time_col in ['Initial_Peak_Time', 'Final_Peak_Time', 'Initial_Peak_Time_w', 'Final_Peak_Time_w']:
    for peak_time in df_csv[time_col]:
        peak_time_dt = pd.to_datetime(peak_time)
        if time1.min() <= peak_time_dt <= time1.max():
            axs[0].axvline(x=peak_time_dt, color=event_colors[time_col], linestyle='-')
        if time2.min() <= peak_time_dt <= time2.max():
            axs[1].axvline(x=peak_time_dt, color=event_colors[time_col], linestyle='-')

# Légende
legend_elements = [
    plt.Line2D([0], [0], color=event_colors['Stra'], lw=2, label='STRA'),
    plt.Line2D([0], [0], color=event_colors['Stre'], lw=2, label='STRE'),
    plt.Line2D([0], [0], color=event_colors['Filtered'], lw=2, linestyle='--', label='Glissement de terrain (Filtré)'),
    plt.Line2D([0], [0], color=event_colors['Unfiltered'], lw=2, linestyle='--', label='Glissement de terrain (Non filtré)'),
    plt.Line2D([0], [0], color=event_colors['Initial_Peak_Time'], lw=2, label='Initial_Peak_Time'),
    plt.Line2D([0], [0], color=event_colors['Final_Peak_Time'], lw=2, label='Final_Peak_Time'),
    plt.Line2D([0], [0], color=event_colors['Initial_Peak_Time_w'], lw=2, label='Initial_Peak_Time_w'),
    plt.Line2D([0], [0], color=event_colors['Final_Peak_Time_w'], lw=2, label='Final_Peak_Time_w'),
]

axs[0].legend(handles=legend_elements, loc='upper right')
plt.tight_layout()
plt.show()
