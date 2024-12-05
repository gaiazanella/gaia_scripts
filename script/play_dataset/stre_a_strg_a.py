import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client


# Chemin vers le fichier CSV
file_path_stre_a = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/all_peaks.csv'
file_path_strg_a = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra/strg_stra_all_peaks_data.csv'

# Lire le fichier CSV
data_stre_a = pd.read_csv(file_path_stre_a)
data_strg_a = pd.read_csv(file_path_strg_a)

# Afficher les premières lignes
print(data_stre_a.head())
print(data_strg_a.head())

data_stre_a['Peak_Time_UTC'] = pd.to_datetime(data_stre_a['Peak_Time_UTC'])
data_strg_a['Peak_Time_UTC'] = pd.to_datetime(data_strg_a['Peak_Time_UTC'])

# Créer une figure avec 3 subplots sur une colonne (3 lignes, 1 colonne)
fig, axs = plt.subplots(2, 1, figsize=(8, 12))  # 3 lignes, 1 colonne

# Subplot 1 : Sin(x)
axs[0].plot(data_stre_a['Peak_Time_UTC'], data_stre_a['Ratio'], label='RSAM(STRE)/RSAM(STRA)', color='orange')
#axs[0].set_title('Sin(x)')
axs[0].legend()
axs[0].grid(True)

# Subplot 2 : Cos(x)
axs[1].plot(data_strg_a['Peak_Time_UTC'], data_strg_a['Ratio'], label='RSAM(STRG)/RSAM(STRA)', color='green')
#axs[1].set_title('Cos(x)')
axs[1].legend()
axs[1].grid(True)


# Afficher les graphiques
plt.show()