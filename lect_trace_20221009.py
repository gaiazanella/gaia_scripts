from obspy import Stream
## PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')  # ou 'TkAgg' selon ton système
import matplotlib.pyplot as plt

# Paramètres
db = '/mnt/bigmama3'
net = ['I*']
channel = ['*HZ']#
#ti = UTCDateTime("2022-10-09T07:00:40")
#ti = UTCDateTime("2022-12-04T15:00:00")
#ti = UTCDateTime("2019-07-03T14:00:00")

#ti = UTCDateTime("2019-07-03T14:44:00")
#ti = UTCDateTime("2019-08-28T10:16:00")
#ti = UTCDateTime("2020-11-16T09:17:00")
#ti = UTCDateTime("2021-05-19T12:50:00")
ti = UTCDateTime("2022-10-09T07:21:40")
#ti = UTCDateTime("2022-12-04T15:17:00")

#tf = ti + (60 * 60 * 1) # 1 heure de données
#tf= ti+ (60*60)*1 # 1h
tf = ti + (4*60) # 4 min
#tf = ti + (15*60) # 15 min
#channel = ['*H*']

#t1 = UTCDateTime("2022-10-09T07:23:10")
#t2 = UTCDateTime("2022-10-09T07:23:30")
#t1 = UTCDateTime("2022-10-09T07:23:08") #ti FB
#t2 = UTCDateTime("2022-10-09T07:23:30") #tf FB
#t1 = UTCDateTime("2022-12-04T15:18:12") #ti FB
#t2 = UTCDateTime("2022-12-04T15:18:24") #tf FB
#t1 = UTCDateTime("2022-12-04T15:18:10")
#t2 = UTCDateTime("2022-12-04T15:18:20")
ti_bol = UTCDateTime("2022-10-09T07:22:42")
ts_fb = UTCDateTime("2022-10-09T07:22:50")
tf_fb_z500_b1 = UTCDateTime("2022-10-09T07:23:08") #ti FB
t_z_z200_c2 = UTCDateTime("2022-10-09T07:23:20")
te_fb_z0_d3 = UTCDateTime("2022-10-09T07:23:30") #tf FB

# Client pour récupérer les données
client = Client(db)
stations = ['STRA', 'STRE', 'STRG', 'STRC']
st1 = Stream()

for network in net:
    for sta in stations:
        st = client.get_waveforms(
            network=network,
            station=sta,
            location="",
            channel=channel[0],
            starttime=ti,
            endtime=tf
        )
        st1 += st

print(st1)
#st1.plot()

# Facteurs de conversion selon le réseau
conv_IT = 3.2e-6 / 800
conv_IV = 1e-6 / 1200

# Appliquer le facteur à chaque trace
for tr in st1:
    if tr.stats.network == "IT":
        tr.data = tr.data.astype(np.float64) * conv_IT

    elif tr.stats.network == "IV":
        tr.data = tr.data.astype(np.float64) * conv_IV

    else:
        print(f"Réseau inconnu : {tr.stats.network}")

print("Conversion appliquée")

# Les cinq temps à représenter
temps = [
    ti_bol,
    ts_fb,
    tf_fb_z500_b1,
    t_z_z200_c2,
    te_fb_z0_d3
]

labels = [
    "ti_bol",
    "ts_fb",
    "tf_fb_z500_b1",
    "t_z_z200_c2",
    "te_fb_z0_d3"
]

colors = ["darkorange", "lime", "black", "blue", "magenta"]

# Tracer les données sismiques
fig = st1.plot(show=False, handle=True)

# Ajouter les lignes verticales sur toutes les traces
for ax in fig.axes:
    for t, label, color in zip(temps, labels, colors):
        ax.axvline(
            x=t.matplotlib_date,
            color=color,
            linestyle="--",
            linewidth=1.5,
            label=label
        )

# Afficher la légende une seule fois
fig.axes[0].legend(loc="upper right", fontsize=8)

plt.show()

