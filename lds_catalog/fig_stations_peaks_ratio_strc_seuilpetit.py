##### copie de stre_a_strg_g_daily_vero_plot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client

# Chemin vers le fichier CSV contenant les ratios
file_path = '/home/gaia/Documents/processing_10_sec/2020/rsam_ratio_test/ratio_rsam_stra_stre_strg_strc_20200628.csv'

# Charger le fichier CSV dans un DataFrame
data_csv = pd.read_csv(file_path)

# Convertir la colonne 'time_UTC' en format datetime
data_csv['time_UTC'] = pd.to_datetime(data_csv['time_UTC'])

# Afficher les premières lignes pour vérifier le contenu
#print("Contenu du fichier CSV des ratios :")
#print(data_csv.head())

# Charger le fichier CSV contenant les données des pics STRE/STRA
peaks_file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra_test/stre_stra_peaks_data_20200628.csv'
peaks_data = pd.read_csv(peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
peaks_data['Peak_Time_UTC'] = pd.to_datetime(peaks_data['Peak_Time_UTC'])
peaks_data['Initial_Peak_Time'] = pd.to_datetime(peaks_data['Initial_Peak_Time'])
peaks_data['Final_Peak_Time'] = pd.to_datetime(peaks_data['Final_Peak_Time'])
peaks_data['Initial_Peak_Time_w'] = pd.to_datetime(peaks_data['Initial_Peak_Time_w'])
peaks_data['Final_Peak_Time_w'] = pd.to_datetime(peaks_data['Final_Peak_Time_w'])

# Afficher les premières lignes pour vérifier le contenu des pics
#print("Contenu du fichier CSV des pics STRE/STRA : :")
#print(peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRG/STRA
strg_stra_peaks_file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra_test/strg_stra_peaks_data_20200628.csv'
strg_stra_peaks_data = pd.read_csv(strg_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strg_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strg_stra_peaks_data['Peak_Time_UTC'])
strg_stra_peaks_data['Initial_Peak_Time'] = pd.to_datetime(strg_stra_peaks_data['Initial_Peak_Time'])
strg_stra_peaks_data['Final_Peak_Time'] = pd.to_datetime(strg_stra_peaks_data['Final_Peak_Time'])
strg_stra_peaks_data['Initial_Peak_Time_w'] = pd.to_datetime(strg_stra_peaks_data['Initial_Peak_Time_w'])
strg_stra_peaks_data['Final_Peak_Time_w'] = pd.to_datetime(strg_stra_peaks_data['Final_Peak_Time_w'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRG/STRA
#print("Contenu du fichier CSV des pics STRG/STRA :")
#print(strg_stra_peaks_data.head())

# Charger le fichier CSV contenant les données des pics pour STRG/STRA ## CHANGEMENTS POUR STRC J'AI PRIS THTR=0.05
strc_stra_peaks_file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strc_stra_test_0.05/strc_stra_peaks_data_20200628.csv'
strc_stra_peaks_data = pd.read_csv(strc_stra_peaks_file_path)

# Convertir la colonne 'Peak_Time_UTC' en format datetime
strc_stra_peaks_data['Peak_Time_UTC'] = pd.to_datetime(strc_stra_peaks_data['Peak_Time_UTC'])
strc_stra_peaks_data['Initial_Peak_Time'] = pd.to_datetime(strc_stra_peaks_data['Initial_Peak_Time'])
strc_stra_peaks_data['Final_Peak_Time'] = pd.to_datetime(strc_stra_peaks_data['Final_Peak_Time'])
strc_stra_peaks_data['Initial_Peak_Time_w'] = pd.to_datetime(strc_stra_peaks_data['Initial_Peak_Time_w'])
strc_stra_peaks_data['Final_Peak_Time_w'] = pd.to_datetime(strc_stra_peaks_data['Final_Peak_Time_w'])

# Afficher les premières lignes pour vérifier le contenu des pics de STRG/STRA
#print("Contenu du fichier CSV des pics STRC/STRA :")
#print(strg_stra_peaks_data.head())

# Configuration pour récupérer les données sismiques
db = '/mnt/bigmama3'
stations = ['STRE', 'STRA', 'STRG', 'STRC']  # Ajouter STRG
network = '*'  # Accepter tous les réseaux
channel = '*HZ'  # Composante Z
fs = 50  # Fréquence d'échantillonnage cible

client = Client(db)

# Période d'intérêt
ti = UTCDateTime("2020-06-28T00:00:00.000")
tf = ti + 60 * 60 * 24  # Une journée complète

# Récupérer et prétraiter les données pour les trois stations
data_sismique = {}
for station in stations:
    st = client.get_waveforms(network=network, station=station, location="", channel=channel, starttime=ti, endtime=tf)
    #print(f"Données de la station sismique {station} récupérées :", st)
    st.merge(fill_value='interpolate')
    st.detrend("demean")
    st.detrend("linear")
    if station == 'STRE':
        # Filtrage pour STRE (8–15 Hz)
        data_sismique['STRE'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRA':
        # Filtrage pour STRA (0.03–1 Hz)
        data_sismique['STRA_vlp'] = bandpass(st[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
        data_sismique['STRA_hf'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)    
    elif station == 'STRG':  # Ajouter le traitement pour STRG
        # Filtrage pour STRG (8-15 Hz)
        data_sismique['STRG'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRC':  # Ajouter le traitement pour STRG
        # Filtrage pour STRC (8-15 Hz)
        data_sismique['STRC'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)

    # Créer un axe temporel pour chaque station
    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[f'{station}_time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(len(st[0].data)) / fs, unit='s'))

# Calculer les valeurs min et max des 3 premiers signaux
y_min = min(np.min(data_sismique['STRA_vlp']),np.min(data_sismique['STRA_hf']), np.min(data_sismique['STRE']), np.min(data_sismique['STRG']), np.min(data_sismique['STRC']))
y_max = max(np.max(data_sismique['STRA_vlp']),np.max(data_sismique['STRA_hf']), np.max(data_sismique['STRE']), np.max(data_sismique['STRG']), np.min(data_sismique['STRC']))

# Calculer les limites min et max des deux ratios
ratio_min = min(np.min(data_csv['Ratio_STRE_STRA']), np.min(data_csv['Ratio_STRG_STRA']))
ratio_max = max(np.max(data_csv['Ratio_STRE_STRA']), np.max(data_csv['Ratio_STRG_STRA']))

# Créer une figure avec cinq sous-graphiques (subplots) empilés, en partageant l'axe X
fig, ax = plt.subplots(8, 1, figsize=(12, 15), sharex=True)  # 5 sous-graphes

# Premier graphique : Données filtrées pour STRA (0.03-1 Hz)
ax[0].plot(data_sismique['STRA_time'], data_sismique['STRA_vlp'], color='red', label='STRA (0.03-1 Hz)')
ax[0].set_ylabel('RSAM (counts)')
ax[0].set_ylim(-1000, 1000)
#ax[0].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[0].legend(loc='upper right')
for peak_time in peaks_data['Initial_Peak_Time']:
    ax[0].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time']:
    ax[0].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Initial_Peak_Time_w']:
    ax[0].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time_w']:
    ax[0].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
ax[0].grid(True)

# Premier graphique : Données filtrées pour STRA (8-15 Hz)
ax[1].plot(data_sismique['STRA_time'], data_sismique['STRA_hf'], color='red', label='STRA (8-15 Hz)')
ax[1].set_ylabel('RSAM (counts)')
ax[1].set_ylim(-7000, 7000)
#ax[1].set_ylim(-2000, 2000)
#ax[0].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[1].legend(loc='upper right')
for peak_time in peaks_data['Initial_Peak_Time']:
    ax[1].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time']:
    ax[1].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Initial_Peak_Time_w']:
    ax[1].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time_w']:
    ax[1].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
ax[1].grid(True)

# Deuxième graphique : Données filtrées pour STRE (8-15 Hz)
ax[2].plot(data_sismique['STRE_time'], data_sismique['STRE'], color='blue', label='STRE (8-15 Hz)')
ax[2].set_ylabel('RSAM (counts)')
ax[2].set_ylim(-7000, 7000)
#ax[1].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
ax[2].legend(loc='upper right')
for peak_time in peaks_data['Initial_Peak_Time']:
    ax[2].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time']:
    ax[2].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Initial_Peak_Time_w']:
    ax[2].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time_w']:
    ax[2].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
ax[2].grid(True)

# Troisième graphique : Données filtrées pour STRG (8-15 Hz) - avec couleur magenta
ax[3].plot(data_sismique['STRG_time'], data_sismique['STRG'], color='magenta', label='STRG (8-15 Hz)')
ax[3].set_ylabel('RSAM (counts)')
ax[3].set_ylim(-7000, 7000)
#ax[2].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
for strg_stra_peak_time in strg_stra_peaks_data['Initial_Peak_Time']:
    ax[3].axvline(x=strg_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Final_Peak_Time']:
    ax[3].axvline(x=strg_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Initial_Peak_Time_w']:
    ax[3].axvline(x=strg_stra_peak_time, color='blue', linestyle='-', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Final_Peak_Time_w']:
    ax[3].axvline(x=strg_stra_peak_time, color='blue', linestyle='-', linewidth=1)
ax[3].legend(loc='upper right')
ax[3].grid(True)

# Troisième graphique : Données filtrées pour STRC (8-15 Hz) - avec couleur magenta
ax[4].plot(data_sismique['STRC_time'], data_sismique['STRC'], color='cyan', label='STRC (8-15 Hz)')
ax[4].set_ylabel('RSAM (counts)')
ax[4].set_ylim(-7000, 7000)
#ax[3].set_ylim(y_min, y_max)  # Appliquer les mêmes limites pour l'axe y
for strc_stra_peak_time in strc_stra_peaks_data['Initial_Peak_Time']:
    ax[4].axvline(x=strc_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Final_Peak_Time']:
    ax[4].axvline(x=strc_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Initial_Peak_Time_w']:
    ax[4].axvline(x=strc_stra_peak_time, color='blue', linestyle='-', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Final_Peak_Time_w']:
    ax[4].axvline(x=strc_stra_peak_time, color='blue', linestyle='-', linewidth=1)
ax[4].legend(loc='upper right')
ax[4].grid(True)

# Quatrième graphique : Ratio STRE/STRA (E/A)
ax[5].plot(data_csv['time_UTC'], data_csv['Ratio_STRE_STRA'], color='orange', label='STRE/STRA')
ax[5].set_ylabel('Ratio')
ax[5].set_ylim(0, 4)
#ax[5].set_ylim(ratio_min, ratio_max)  # Appliquer les mêmes limites pour l'axe y
ax[5].legend(loc='upper right')
ax[5].legend(loc='upper right')
ax[5].grid(True)

filtered_peaks_red = peaks_data[(peaks_data['RSAM_E'] > 875) & (peaks_data['Ratio'] < 6.5)]
filtered_peaks_black = peaks_data[~((peaks_data['RSAM_E'] > 875) & (peaks_data['Ratio'] < 6.5))]

# Affichage des étoiles rouges (pour les pics filtrés)
ax[5].scatter(filtered_peaks_red['Peak_Time_UTC'], filtered_peaks_red['Ratio'], color='black', marker='*', label='Detection (E/A) - Filtered')
print(len(filtered_peaks_red['Ratio']))
print(filtered_peaks_red['Peak_Time_UTC'])

# Affichage des étoiles noires (pour les autres pics)
ax[5].scatter(filtered_peaks_black['Peak_Time_UTC'], filtered_peaks_black['Ratio'], color='red', marker='*', label='Detection (E/A) - Not filtered')

# Ajouter des étoiles basées sur les pics du fichier peaks_data.csv
#ax[3].scatter(peaks_data['Peak_Time_UTC'], peaks_data['Ratio'], color='red', marker='*', label='Detection (E/A)')
for peak_time in peaks_data['Initial_Peak_Time']:
    ax[5].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time']:
    ax[5].axvline(x=peak_time, color='black', linestyle='--', linewidth=1)
for peak_time in peaks_data['Initial_Peak_Time_w']:
    ax[5].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
for peak_time in peaks_data['Final_Peak_Time_w']:
    ax[5].axvline(x=peak_time, color='black', linestyle='-', linewidth=1)
ax[5].legend()

# Cinquième graphique : Ratio STRG/STRA (G/A)
ax[6].plot(data_csv['time_UTC'], data_csv['Ratio_STRG_STRA'], color='green', label='STRG/STRA')
ax[6].set_ylabel('Ratio')
ax[6].set_ylim(0, 2)
#ax[4].set_ylim(ratio_min, ratio_max)  # Appliquer les mêmes limites pour l'axe y
ax[6].legend(loc='upper right')
ax[6].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strg_stra_peaks_data.csv
ax[6].scatter(strg_stra_peaks_data['Peak_Time_UTC'], strg_stra_peaks_data['Ratio'], color='blue', marker='*', label='Detection (G/A)')
for strg_stra_peak_time in strg_stra_peaks_data['Initial_Peak_Time']:
    ax[6].axvline(x=strg_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Final_Peak_Time']:
    ax[6].axvline(x=strg_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Initial_Peak_Time_w']:
    ax[6].axvline(x=strg_stra_peak_time, color='blue', linestyle='-', linewidth=1)
for strg_stra_peak_time in strg_stra_peaks_data['Final_Peak_Time_w']:
    ax[6].axvline(x=strg_stra_peak_time, color='blue', linestyle='-', linewidth=1)
ax[6].legend(loc='upper right')

# Cinquième graphique : Ratio STRG/STRA (G/A)
ax[7].plot(data_csv['time_UTC'], data_csv['Ratio_STRC_STRA'], color='purple', label='STRC/STRA')
ax[7].set_ylabel('Ratio')
ax[7].set_ylim(0, 1)
#ax[7].set_ylim(ratio_min, ratio_max)  # Appliquer les mêmes limites pour l'axe y
ax[7].legend(loc='upper right')
ax[7].grid(True)

# Ajouter des étoiles basées sur les pics du fichier strg_stra_peaks_data.csv
ax[7].scatter(strc_stra_peaks_data['Peak_Time_UTC'], strc_stra_peaks_data['Ratio'], color='blue', marker='*', label='Detection (C/A)')
for strc_stra_peak_time in strc_stra_peaks_data['Initial_Peak_Time']:
    ax[7].axvline(x=strc_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Final_Peak_Time']:
    ax[7].axvline(x=strc_stra_peak_time, color='blue', linestyle='--', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Initial_Peak_Time_w']:
    ax[7].axvline(x=strc_stra_peak_time, color='blue', linestyle='-', linewidth=1)
for strc_stra_peak_time in strc_stra_peaks_data['Final_Peak_Time_w']:
    ax[7].axvline(x=strc_stra_peak_time, color='blue', linestyle='-', linewidth=1)
ax[7].legend(loc='upper right')

# Ajuster l'espacement entre les sous-graphiques
plt.tight_layout()

# Afficher les graphiques
plt.show()
