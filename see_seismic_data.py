### PACKAGES
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import numpy as np   # 🔑 nécessaire pour NaN
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# =====================
# Paramètres généraux
# =====================
db = '/mnt/bigmama3'
client = Client(db)

station = 'STRA'
network = 'I*'
channel = '*HZ'
location = ""

duration = 4 * 60  # 4 minutes

# =====================
# Dates / heures
# =====================
times = [
    UTCDateTime("2019-07-03T14:44:00"),
    UTCDateTime("2019-08-28T10:16:00"),
    UTCDateTime("2020-11-16T09:17:00"),
    UTCDateTime("2021-05-19T12:50:00"),
    UTCDateTime("2022-10-09T07:21:40"),
    UTCDateTime("2022-12-04T15:17:00"),
]

# =====================
# Figure
# =====================
fig, axes = plt.subplots(6, 1, figsize=(12, 8), sharex=False)

for i, ti in enumerate(times):
    tf = ti + duration

    st = client.get_waveforms(
    network=network,
    station=station,
    location=location,
    channel=channel,
    starttime=ti,
    endtime=tf
)

# 🔑 autoriser NaN
    for tr in st:
        tr.data = tr.data.astype(float)

# 🔑 blancs dans les gaps
    st.merge(method=1, fill_value=np.nan)
    st.trim(ti, tf, pad=True, fill_value=np.nan)

    tr = st[0]

    # 🔑 FILTRAGE 8–15 Hz
    tr.filter("bandpass", freqmin=8, freqmax=15, corners=4, zerophase=True)

    t = tr.times() / 60.0
    axes[i].plot(t, tr.data, 'k', linewidth=0.8)
    axes[i].set_ylabel("Amplitude (counts)")

axes[-1].set_xlabel("Time (minutes)")
plt.tight_layout()
plt.show()

### PACKAGES
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import numpy as np

# =====================
# Paramètres généraux
# =====================
db = '/mnt/bigmama3'
client = Client(db)

station = 'STRA'
network = 'I*'
channel = '*HZ'
location = ""

duration = 4 * 60  # 4 minutes


# =====================
# Première boucle : récupérer toutes les traces filtrées et trouver max Y
# =====================
filtered_traces = []
ymax = 0

for ti in times:
    tf = ti + duration

    st = client.get_waveforms(
        network=network,
        station=station,
        location=location,
        channel=channel,
        starttime=ti,
        endtime=tf
    )

    # convertir en float pour NaN
    for tr in st:
        tr.data = tr.data.astype(float)

    st.merge(method=1, fill_value=np.nan)
    st.trim(ti, tf, pad=True, fill_value=np.nan)

    tr = st[0]
    print(tr)

    # filtrage 8-15 Hz sans supprimer les NaN
    mask = np.isnan(tr.data)
    tr.data[mask] = 0
    tr.filter("bandpass", freqmin=8, freqmax=15, corners=4, zerophase=True)
    tr.data[mask] = np.nan

    # 🔹 Conversion counts → m/s
    #tr.data = tr.data / 2.4390e8
    conv=3.2e-6/800
    tr.data = tr.data*conv

    filtered_traces.append(tr)
    #ymax = max(ymax, np.nanmax(np.abs(tr.data)))

# =====================
# Deuxième boucle : plot avec la même échelle Y
# =====================
fig, axes = plt.subplots(len(times), 1, figsize=(12, 8), sharex=True)

for i, tr in enumerate(filtered_traces):
    t = tr.times() / 60.0  # temps en minutes
    axes[i].plot(t, tr.data, 'k', linewidth=0.8)
    axes[i].set_ylabel("Amplitude (m/s)")
    axes[i].set_ylim([-5e-4, 5e-4])
    axes[i].yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    axes[i].ticklabel_format(axis='y', style='scientific', scilimits=(0,0))    

axes[-1].set_xlabel("Time (minutes)")
for ax in axes[:-1]:
    ax.label_outer()
plt.tight_layout()
plt.show()

###
# =====================

raw_traces = []
filtered_traces = []

for ti in times:
    tf = ti + duration

    st = client.get_waveforms(
        network=network,
        station=station,
        location=location,
        channel=channel,
        starttime=ti,
        endtime=tf
    )

    for tr in st:
        tr.data = tr.data.astype(float)

    st.merge(method=1, fill_value=np.nan)
    st.trim(ti, tf, pad=True, fill_value=np.nan)

    # trace normale
    tr_raw = st[0].copy()

    # trace filtrée
    tr_filt = st[0].copy()

    mask = np.isnan(tr_filt.data)
    tr_filt.data[mask] = 0

    tr_filt.filter(
        "bandpass",
        freqmin=8,
        freqmax=15,
        corners=4,
        zerophase=True
    )

    tr_filt.data[mask] = np.nan

    # conversion counts -> m/s
    conv = 3.2e-6 / 800
    tr_raw.data = tr_raw.data * conv
    tr_filt.data = tr_filt.data * conv

    raw_traces.append(tr_raw)
    filtered_traces.append(tr_filt)


fig, axes = plt.subplots(len(times), 1, figsize=(12, 8), sharex=True)

for i, (tr_raw, tr_filt) in enumerate(zip(raw_traces, filtered_traces)):

    t = tr_raw.times() / 60.0

    axes[i].plot(t, tr_raw.data, color='0.7', linewidth=0.8, label='Non filtrée')
    axes[i].plot(t, tr_filt.data, 'k', linewidth=1.0, label='Filtrée 8–15 Hz')

    axes[i].set_ylabel("Amplitude (m/s)")
    axes[i].set_ylim([-5e-4, 5e-4])

    axes[i].yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    axes[i].ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))

    #if i == 0:
    #    axes[i].legend(loc='upper right')

axes[-1].set_xlabel("Time (minutes)")

for ax in axes[:-1]:
    ax.label_outer()

plt.tight_layout()
plt.show()