import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-01-01T00:00:00.000")
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

# Convertir les temps en datetime en évitant l'erreur de numpy.ndarray
time1 = pd.to_datetime(st1[0].stats.starttime) + pd.to_timedelta(np.arange(0, len(st1[0].data)) / fs, unit='s')
time2 = pd.to_datetime(st2[0].stats.starttime) + pd.to_timedelta(np.arange(0, len(st2[0].data)) / fs, unit='s')

# Lire le fichier CSV contenant les événements
csv_file = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed/peaks_data_20200101.csv'
df_csv = pd.read_csv(csv_file)

# Convertir les colonnes en format datetime
df_csv['Peak_Time_UTC'] = pd.to_datetime(df_csv['Peak_Time_UTC'])

# Charger les fichiers CSV pour RSAM (STRA et STRE)
rsam_stra_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRA_20200101.csv'
rsam_stre_file = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRE_20200101.csv'

rsam_stra = pd.read_csv(rsam_stra_file)
rsam_stre = pd.read_csv(rsam_stre_file)

# Convertir 'time_UTC' en datetime
rsam_stra['time_UTC'] = pd.to_datetime(rsam_stra['time_UTC'])
rsam_stre['time_UTC'] = pd.to_datetime(rsam_stre['time_UTC'])

# Calculer le rapport entre les RSAM de STRE et STRA (STRE / STRA)
rsam_ratio = rsam_stre['RSAM_env_smooth_8-15Hz'] / rsam_stra['RSAM_env_smooth_8-15Hz']

# Création de la figure avec 4 subplots
fig, axs = plt.subplots(4, 1, figsize=(12, 22), sharex=True)

# Subplot 1 : Trace des données de STRA et STRE
axs[0].plot(time1, st1[0].data, color='red', label='STRA')
axs[0].plot(time2, st2[0].data, color='blue', label='STRE')
axs[0].set_ylabel('Amplitude')
axs[0].grid(True)

# Subplot 2 : Même chose (non filtré)
axs[1].plot(time1, st1[0].data, color='red', label='STRA')
axs[1].plot(time2, st2[0].data, color='blue', label='STRE')
axs[1].set_ylabel('Amplitude')
axs[1].grid(True)

# Subplot 3 : RSAM de chaque station (STRA et STRE)
axs[2].plot(rsam_stra['time_UTC'], rsam_stra['RSAM_env_smooth_8-15Hz'], color='red', label='RSAM (STRA)')
axs[2].plot(rsam_stre['time_UTC'], rsam_stre['RSAM_env_smooth_8-15Hz'], color='blue', label='RSAM (STRE)')
axs[2].set_ylabel('RSAM (8-15 Hz)')
axs[2].grid(True)

# Subplot 4 : Rapport entre les RSAM de STRE et STRA
axs[3].plot(rsam_stra['time_UTC'], rsam_ratio, color='orange')
axs[3].set_ylabel('RSAM(STRE) / RSAM(STRA)')
axs[3].grid(True)

# Ajouter des lignes verticales uniquement pour les glissements de terrain
event_colors = {
    'filtered': 'lime',  # Vert pour les événements filtrés
    'non_filtered': 'darkgreen',  # Vert foncé pour les non filtrés
}

# Filtrer les événements en fonction des conditions
filtered_events = df_csv[(df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5)]
non_filtered_events = df_csv[~((df_csv['RSAM_E'] > 875) & (df_csv['Ratio'] < 6.5))]

# Ajouter des lignes verticales pour les événements de glissement de terrain
for event_set, color, label in [(filtered_events, event_colors['filtered'], 'Filtered Landslide'),
                                (non_filtered_events, event_colors['non_filtered'], 'Landslide')]:
    for peak_time in event_set['Peak_Time_UTC']:
        peak_time_dt = pd.to_datetime(peak_time)
        # Ajouter des lignes verticales dans tous les subplots
        axs[0].axvline(x=peak_time_dt, color=color, linestyle='--')
        axs[1].axvline(x=peak_time_dt, color=color, linestyle='--')
        axs[2].axvline(x=peak_time_dt, color=color, linestyle='--')
        axs[3].axvline(x=peak_time_dt, color=color, linestyle='--')

# Ajouter une légende et une étiquette d'axe
axs[3].set_xlabel('Time (UTC)')
fig.tight_layout()

# Afficher la légende
axs[0].legend(loc='upper right')

# Affichage
plt.show()
