### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE', 'STRG']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Fréquence cible

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-03-28T15:45:00.000")
tf = ti + (60 * 60 * 2 * 1)  # 2 heure de données

# Récupérer les données pour les trois stations
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
ste = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)
stg = client.get_waveforms(network=net[1], station=stz[2], location="", channel=channel[1], starttime=ti, endtime=tf)

# Vérification des données récupérées
if len(sta) == 0:
    print(f"Aucune donnée récupérée pour la station {stz[0]}")
else:
    print(f"Nombre de traces pour {stz[0]}: {len(sta)}")

if len(ste) == 0:
    print(f"Aucune donnée récupérée pour la station {stz[1]}")
else:
    print(f"Nombre de traces pour {stz[1]}: {len(ste)}")

if len(stg) == 0:
    print(f"Aucune donnée récupérée pour la station {stz[2]}")
else:
    print(f"Nombre de traces pour {stz[2]}: {len(stg)}")

# Fusionner les données (interpolation) si elles existent
if len(sta) > 0:
    sta.merge(fill_value='interpolate')
    sta.detrend("demean")
    sta.detrend("linear")

if len(ste) > 0:
    ste.merge(fill_value='interpolate')
    ste.detrend("demean")
    ste.detrend("linear")

if len(stg) > 0:
    stg.merge(fill_value='interpolate')
    stg.detrend("demean")
    stg.detrend("linear")

# Appliquer un filtre bandpass sur les données
if len(sta) > 0:
    dataa = sta[0].data
    dataa = dataa * ((3.2 * 10**(-6)) / 800)
    dataa1 = bandpass(dataa, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
    dataavlp = bandpass(dataa, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
else:
    dataa = dataa1 = dataavlp = None

if len(ste) > 0:
    datae = ste[0].data
    datae = datae * ((3.2 * 10**(-6)) / 800)
    datae1 = bandpass(datae, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
    dataevlp = bandpass(datae, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
else:
    datae = datae1 = dataevlp = None

if len(stg) > 0:
    datag = stg[0].data
    datag = datag * ((3.2 * 10**(-6)) / 800)
    datag1 = bandpass(datag, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
    datagvlp = bandpass(datag, freqmin=0.03, freqmax=1, df=fs, corners=4, zerophase=True)
else:
    datag = datag1 = datagvlp = None

# Convertir les temps en datetime
if len(sta) > 0:
    starttimea = UTCDateTime(sta[0].stats.starttime).datetime
    timea = pd.to_datetime(starttimea + pd.to_timedelta(np.arange(0, len(dataa) / fs, 1 / fs), unit='s'))
else:
    timea = None

if len(ste) > 0:
    starttimee = UTCDateTime(ste[0].stats.starttime).datetime
    timee = pd.to_datetime(starttimee + pd.to_timedelta(np.arange(0, len(datae) / fs, 1 / fs), unit='s'))
else:
    timee = None

if len(stg) > 0:
    starttimeg = UTCDateTime(stg[0].stats.starttime).datetime
    timeg = pd.to_datetime(starttimeg + pd.to_timedelta(np.arange(0, len(datag) / fs, 1 / fs), unit='s'))
else:
    timeg = None

# Création des subplots (4 sous-graphiques)
fig, axs = plt.subplots(4, 1, figsize=(12, 16), sharex=True)

# 1er subplot pour les stations STRA et STRE
if timea is not None and timee is not None:
    axs[0].plot(timea, dataavlp, label=f"{stz[0]}", color='r')
    axs[0].plot(timee, dataevlp, label=f"{stz[1]}", color='b')
    if timeg is not None:
        axs[0].plot(timee, datagvlp, label=f"{stz[2]}", color='magenta')
    axs[0].set_ylabel('RSAM (m/s) 0.03-1Hz')
    axs[0].legend()
    axs[0].grid(True)

# Calcul de la valeur maximale absolue entre les deux datasets
max_val = 0
if dataa1 is not None:
    max_val = max(max_val, max(abs(dataa1)))
if datae1 is not None:
    max_val = max(max_val, max(abs(datae1)))
if datag1 is not None:
    max_val = max(max_val, max(abs(datag1)))

# 2ème subplot pour la station STRA
if timea is not None and dataa1 is not None:
    axs[1].plot(timea, dataa1, color='r')
    axs[1].set_ylabel('RSAM (m/s) 0.03-24Hz')
    axs[1].grid(True)
    axs[1].set_ylim(-max_val, max_val)  # Uniformiser les limites de y

# 3ème subplot pour la station STRE
if timee is not None and datae1 is not None:
    axs[2].plot(timee, datae1, color='b')
    axs[2].set_ylabel('RSAM (m/s) 0.03-24Hz')
    axs[2].grid(True)
    axs[2].set_ylim(-max_val, max_val)  # Uniformiser les limites de y

# 4ème subplot pour le spectrogramme de la station STRA
if timeg is not None and datag1 is not None:
    axs[3].plot(timeg, datag1, color='magenta')
    axs[3].set_ylabel('RSAM (m/s) 0.03-24Hz')
    axs[3].grid(True)
    axs[3].set_ylim(-max_val, max_val)

# Ajuster la disposition des subplots
plt.tight_layout()
plt.show()
