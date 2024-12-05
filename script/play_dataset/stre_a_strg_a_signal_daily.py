import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
from obspy.clients.filesystem.sds import Client


# Chemin vers le fichier CSV
file_path_stre_a = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/peaks_data_20200105.csv'
file_path_strg_a = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra/strg_stra_peaks_data_20200105.csv'

# Lire le fichier CSV
data_stre_a = pd.read_csv(file_path_stre_a)
data_strg_a = pd.read_csv(file_path_strg_a)

# Afficher les premières lignes
print(data_stre_a.head())
print(data_strg_a.head())

# Conversion de 'Peak_Time_UTC' en datetime
data_stre_a['Peak_Time_UTC'] = pd.to_datetime(data_stre_a['Peak_Time_UTC'])
data_strg_a['Peak_Time_UTC'] = pd.to_datetime(data_strg_a['Peak_Time_UTC'])

####################
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE', 'STRG']
net = ['IT', 'IV', 'I*']
channel = ['*HZ']
fs = 50  # Fréquence cible

client = Client(db)
ti = UTCDateTime("2020-01-05T00:00:00.000")
tf = ti + (60 * 60 * 24 * 1)

st = client.get_waveforms(network='*', station=stz[1], location="", channel=channel[0], starttime=ti, endtime=tf)
print(st)
st.merge(fill_value='interpolate')
st.detrend("demean")
st.detrend("linear")
data = st[0].data
data = bandpass(data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

starttime = UTCDateTime(st[0].stats.starttime).datetime
time = pd.to_datetime(starttime + pd.to_timedelta(np.arange(0, len(data) / fs, 1 / fs), unit='s'))

####################

# Créer une figure avec 3 subplots sur une colonne (3 lignes, 1 colonne)
fig, axs = plt.subplots(3, 1, figsize=(8, 12), sharex=True)  # 3 lignes, 1 colonne, partager l'axe x

# Subplot 1 : RSAM(STRE)/RSAM(STRA)
axs[0].plot(data_stre_a['Peak_Time_UTC'], data_stre_a['Ratio'], label='RSAM(STRE)/RSAM(STRA)', color='orange')
axs[0].set_ylabel('RSAM(STRE)/RSAM(STRA)')
axs[0].legend()
axs[0].grid(True)

# Subplot 2 : RSAM(STRG)/RSAM(STRA)
axs[1].plot(data_strg_a['Peak_Time_UTC'], data_strg_a['Ratio'], label='RSAM(STRG)/RSAM(STRA)', color='green')
axs[1].set_ylabel('RSAM(STRG)/RSAM(STRA)')
axs[1].legend()
axs[1].grid(True)

# Subplot 3 : Signal STRE filtré
axs[2].plot(time, data, label='STRE', color='blue')
axs[2].set_xlabel('Date')  # Placer la date sur l'axe x
axs[2].set_ylabel('RSAM(STRE) 0.03-24Hz')
axs[2].legend()
axs[2].grid(True)

# Ajuster l'espacement entre les subplots pour éviter que les labels se chevauchent
plt.tight_layout()

# Afficher les graphiques
plt.show()
