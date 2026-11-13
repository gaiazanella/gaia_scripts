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
    #UTCDateTime("2020-11-16T09:17:00"),
    UTCDateTime("2021-05-19T12:50:00"),
    UTCDateTime("2022-10-09T07:21:40"),
    UTCDateTime("2022-12-04T15:17:00"),
]

# =====================
# Figure
# =====================
fig, axes = plt.subplots(5, 1, figsize=(12, 8), sharex=False)

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


### PACKAGES
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# =====================
# Paramètres généraux
# =====================
db = '/mnt/bigmama3'
client = Client(db)

stations = ['STRA', 'STRE']
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
    #UTCDateTime("2020-11-16T09:17:00"),
    UTCDateTime("2021-05-19T12:50:00"),
    UTCDateTime("2022-10-09T07:21:40"),
    UTCDateTime("2022-12-04T15:17:00"),
]

# =====================
# Récupération et filtrage
# =====================
traces_STRA = []
traces_STRE = []

for ti in times:
    tf = ti + duration

    for station in stations:

        st = client.get_waveforms(
            network=network,
            station=station,
            location=location,
            channel=channel,
            starttime=ti,
            endtime=tf
        )

        if len(st) == 0:
            print(f"Pas de données : {station} - {ti}")
            tr = None

        else:
            # Convertir en float pour NaN
            for tr in st:
                tr.data = tr.data.astype(float)

            # Blancs dans les gaps
            st.merge(method=1, fill_value=np.nan)
            st.trim(ti, tf, pad=True, fill_value=np.nan)

            tr = st[0].copy()
            print(tr)

            # Filtrage 8-15 Hz
            mask = np.isnan(tr.data)
            tr.data[mask] = 0

            tr.filter(
                "bandpass",
                freqmin=8,
                freqmax=15,
                corners=4,
                zerophase=True
            )

            tr.data[mask] = np.nan

            # =====================
            # Conversion counts -> m/s
            # =====================
            if tr.stats.network == "IT":
                conv = 3.2e-6 / 800
            elif tr.stats.network == "IV":
                conv = 1e-6 / 1200
            else:
                raise ValueError(
                    f"Réseau inconnu : {tr.stats.network}"
                )

            tr.data = tr.data * conv

        if station == 'STRA':
            traces_STRA.append(tr)
        elif station == 'STRE':
            traces_STRE.append(tr)

# =====================
# Figure : comparaison STRA / STRE
# =====================
fig, axes = plt.subplots(
    len(times), 1,
    figsize=(12, 8),
    sharex=True
)

for i, (tr_STRA, tr_STRE) in enumerate(
    zip(traces_STRA, traces_STRE)
):

    # STRA en gris
    if tr_STRA is not None:
        t_STRA = (
            tr_STRA.stats.starttime - times[i]
            + tr_STRA.times()
        ) / 60.0

        axes[i].plot(
            t_STRA,
            tr_STRA.data,
            color='0.7',
            linewidth=0.8,
            label='STRA'
        )

    # STRE en noir
    if tr_STRE is not None:
        t_STRE = (
            tr_STRE.stats.starttime - times[i]
            + tr_STRE.times()
        ) / 60.0

        axes[i].plot(
            t_STRE,
            tr_STRE.data,
            color='k',
            linewidth=1.0,
            label='STRE'
        )

    axes[i].set_ylabel("Amplitude (m/s)")
    axes[i].set_ylim([-5e-4, 5e-4])
    axes[i].set_xlim(0, 4)

    axes[i].yaxis.set_major_formatter(
        ticker.ScalarFormatter(useMathText=True)
    )
    axes[i].ticklabel_format(
        axis='y',
        style='scientific',
        scilimits=(0, 0)
    )

    # Date de l'événement
    axes[i].set_title(
        times[i].strftime("%Y-%m-%d %H:%M:%S"),
        fontsize=10
    )

    if i == 0:
        axes[i].legend(loc='upper right')

axes[-1].set_xlabel("Time (minutes)")

for ax in axes[:-1]:
    ax.label_outer()

plt.tight_layout()
plt.show()


### PACKAGES
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np

# =====================
# Paramètres généraux
# =====================
db = '/mnt/bigmama3'
client = Client(db)

station = 'STRE'
network = 'I*'
channel = '*HZ'
location = ""

# =====================
# Dates / heures
# =====================
ti = UTCDateTime("2020-03-28T17:00:00")
tf = UTCDateTime("2020-03-29T00:00:00")

# =====================
# Récupération des données
# =====================
st = client.get_waveforms(
    network=network,
    station=station,
    location=location,
    channel=channel,
    starttime=ti,
    endtime=tf
)

if len(st) == 0:
    raise ValueError("Aucune donnée trouvée pour STRE.")

# Convertir en float pour NaN
for tr in st:
    tr.data = tr.data.astype(float)

# Blancs dans les gaps
st.merge(method=1, fill_value=np.nan)
st.trim(ti, tf, pad=True, fill_value=np.nan)

tr = st[0].copy()
print(tr)

# =====================
# Filtrage 8-15 Hz
# =====================
mask = np.isnan(tr.data)
tr.data[mask] = 0

tr.filter(
    "bandpass",
    freqmin=8,
    freqmax=15,
    corners=4,
    zerophase=True
)

tr.data[mask] = np.nan

# =====================
# Conversion counts -> m/s
# =====================
if tr.stats.network == "IT":
    conv = 3.2e-6 / 800
elif tr.stats.network == "IV":
    conv = 1e-6 / 1200
else:
    raise ValueError(
        f"Réseau inconnu : {tr.stats.network}"
    )

tr.data = tr.data * conv

# =====================
# Figure : 5 subplots
# =====================
fig, axes = plt.subplots(
    5, 1,
    figsize=(12, 8),
    sharex=True
)

# Temps en dates Matplotlib
t = tr.times("matplotlib")

# Quatre premiers subplots vides
for i in range(4):
    axes[i].set_ylabel("Amplitude (m/s)")
    axes[i].set_ylim([-5e-4, 5e-4])

# Cinquième subplot : STRE
axes[4].plot(
    t,
    tr.data,
    color='k',
    linewidth=0.8,
    label='STRE'
)

axes[4].set_ylabel("Amplitude (m/s)")
axes[4].set_ylim([-5e-4, 5e-4])
axes[4].legend(loc='upper right')

# =====================
# Format des axes
# =====================
for ax in axes:
    ax.yaxis.set_major_formatter(
        ticker.ScalarFormatter(useMathText=True)
    )
    ax.ticklabel_format(
        axis='y',
        style='scientific',
        scilimits=(0, 0)
    )

    ax.set_xlim(
        ti.matplotlib_date,
        tf.matplotlib_date
    )

# Axe X en heures UTC
axes[-1].xaxis.set_major_locator(
    mdates.HourLocator(interval=1)
)
axes[-1].xaxis.set_major_formatter(
    mdates.DateFormatter('%H:%M', tz=mdates.UTC)
)

axes[-1].set_xlabel("Time (UTC)")

plt.tight_layout()
plt.show()

### PACKAGES
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.io import loadmat

# =====================
# Chargement des données MATLAB
# =====================
data = loadmat("/home/dario/Scrivania/20021230_data_inter.mat")


t_inter_micron = np.ravel(data["t_inter_micron"])
yoc9 = np.ravel(data["yoc9"])

# =====================
# Conversion secondes -> minutes
# =====================
# Temps relatif : 163 secondes = 0 minute
t = (t_inter_micron - 163) / 60.0

# =====================
# Figure : 5 subplots
# =====================
fig, axes = plt.subplots(5, 1, figsize=(12, 8), sharex=True)

# Quatre premiers subplots vides
for i in range(4):
    axes[i].set_ylabel("Amplitude (m/s)")
    axes[i].set_ylim([-5e-4, 5e-4])

# Cinquième subplot
axes[4].plot(t, yoc9, 'k', linewidth=0.8)

axes[4].set_ylabel("Amplitude (m/s)")
axes[4].set_ylim([-5e-4, 5e-4])

# =====================
# Format des axes
# =====================
for ax in axes:
    ax.set_xlim(0, (1084 - 163) / 60.0)
    ax.yaxis.set_major_formatter(
        ticker.ScalarFormatter(useMathText=True)
    )
    ax.ticklabel_format(
        axis='y',
        style='scientific',
        scilimits=(0, 0)
    )

axes[-1].set_xlabel("Time (minutes)")

for ax in axes[:-1]:
    ax.label_outer()

plt.tight_layout()
plt.show()
