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

# Configuration SDS client
db = '/mnt/bigmama3'
stations = ['STRE', 'STRA', 'STRG', 'STRC'] 
stations = ['STRE', 'STRA', 'STRG'] # Ajout de STRC
network = '*'
channel = '*HZ'
fs = 50  # Hz

client = Client(db)

# Fenêtre temporelle
#ti = UTCDateTime("2020-03-17T01:00:00.000")
ti = UTCDateTime("2020-02-06T15:00:00.000")
tf = ti + 60 * 60 *9 # 24 heures

data_sismique = {}
for station in stations:
    st = client.get_waveforms(network=network, station=station, location="", channel=channel, starttime=ti, endtime=tf)
    print(f"Données de la station sismique {station} récupérées :", st)
    st.merge(fill_value='interpolate')
    st.detrend("demean")
    st.detrend("linear")
    if station == 'STRE':
        data_sismique['STRE'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRA':
        data_sismique['STRA'] = bandpass(st[0].data, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
    elif station == 'STRG':
        data_sismique['STRG'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
    elif station == 'STRC':
        data_sismique['STRC'] = bandpass(st[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)

    starttime = UTCDateTime(st[0].stats.starttime).datetime
    data_sismique[f'{station}_time'] = pd.to_datetime(starttime + pd.to_timedelta(np.arange(len(st[0].data)) / fs, unit='s'))

# Ajouter STRA filtré en 8–15 Hz
st_stra_high = client.get_waveforms(network=network, station='STRA', location="", channel=channel, starttime=ti, endtime=tf)
st_stra_high.merge(fill_value='interpolate')
st_stra_high.detrend("demean")
st_stra_high.detrend("linear")
data_sismique['STRA_8_15'] = bandpass(st_stra_high[0].data, freqmin=8, freqmax=15, df=fs, corners=4, zerophase=True)
starttime_high = UTCDateTime(st_stra_high[0].stats.starttime).datetime
data_sismique['STRA_8_15_time'] = pd.to_datetime(starttime_high + pd.to_timedelta(np.arange(len(st_stra_high[0].data)) / fs, unit='s'))

# Conversion counts → m/s
sconv = 2.4390e8
for key in ['STRA', 'STRE', 'STRG', 'STRA_8_15', 'STRC']:
    if key in data_sismique:
        data_sismique[key] = data_sismique[key] / sconv

# Échelle Y commune
y_min = -14e-5
y_max = 14e-5


# Créer la figure avec 5 sous-graphiques
fig, ax = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

# Subplot 1 : STRA (0.01–1 Hz)
ax[0].plot(data_sismique['STRA_time'], data_sismique['STRA'], color='red', label='STRA (0.01–1 Hz)')
ax[0].set_ylabel('Seismic record (m/s)')
ax[0].legend(loc='upper right')
ax[0].grid(True)

# Subplot 2 : STRA (8–15 Hz)
ax[1].plot(data_sismique['STRA_8_15_time'], data_sismique['STRA_8_15'], color='red', label='STRA (8–15 Hz)')
ax[1].set_ylabel('Seismic record (m/s)')
#ax[1].set_ylim(y_min, y_max)
ax[1].legend(loc='upper right')
ax[1].grid(True)

# Subplot 3 : STRE (8–15 Hz)
ax[2].plot(data_sismique['STRE_time'], data_sismique['STRE'], color='blue', label='STRE (8–15 Hz)')
ax[2].set_ylabel('Seismic record (m/s)')
#ax[2].set_ylim(y_min, y_max)
ax[2].legend(loc='upper right')
ax[2].grid(True)

# Subplot 4 : STRG (8–15 Hz)
ax[3].plot(data_sismique['STRG_time'], data_sismique['STRG'], color='magenta', label='STRG (8–15 Hz)')
ax[3].set_ylabel('Seismic record (m/s)')
#ax[3].set_ylim(y_min, y_max)
ax[3].legend(loc='upper right')
ax[3].grid(True)

# X-axis formatting (sur le dernier subplot)
#ax[3].xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
#ax[3].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#ax[3].xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
#plt.setp(ax[3].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()
