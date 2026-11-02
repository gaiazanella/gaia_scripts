
### PACKAGES
from obspy import UTCDateTime
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# =====================
# Paramètres généraux
# =====================
db = '/mnt/bigmama3'
client = Client(db)

station = 'STRA'
network = 'I*'
channel = '*HZ'
location = ""

# =====================
# Dates / heures
# =====================
ti = UTCDateTime("2020-03-28T15:38:00")
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
print("Nombre de traces :", len(st))
print(st)

# Convertir en float pour NaN
for tr in st:
    tr.data = tr.data.astype(float)

# Blancs dans les gaps
st.merge(method=1, fill_value=np.nan)
st.trim(ti, tf, pad=True, fill_value=np.nan)

tr = st[0]
print(tr)

# =====================
# Deux traces filtrées
# =====================

# Trace filtrée 8-15 Hz
tr_HF = tr.copy()

# Trace filtrée VLP 0.03-0.1 Hz
tr_VLP = tr.copy()

# =====================
# Filtrage 8-15 Hz
# =====================
mask_HF = np.isnan(tr_HF.data)
tr_HF.data[mask_HF] = 0

tr_HF.filter(
    "bandpass",
    freqmin=8,
    freqmax=15,
    corners=4,
    zerophase=True
)

tr_HF.data[mask_HF] = np.nan

# =====================
# Filtrage VLP 0.03-0.1 Hz
# =====================
mask_VLP = np.isnan(tr_VLP.data)
tr_VLP.data[mask_VLP] = 0

tr_VLP.filter(
    "bandpass",
    freqmin=0.03,
    freqmax=0.1,
    corners=4,
    zerophase=True
)

tr_VLP.data[mask_VLP] = np.nan

# =====================
# Conversion counts -> m/s
# =====================
if tr.stats.network == "IT":
    conv = 3.2e-6 / 800
elif tr.stats.network == "IV":
    conv = 1e-6 / 1200
else:
    raise ValueError("Réseau inconnu")

tr_HF.data = tr_HF.data * conv
tr_VLP.data = tr_VLP.data * conv

# =====================
# Figure : 2 subplots
# =====================
fig, axes = plt.subplots(
    2, 1,
    figsize=(14, 7),
    sharex=True
)

# Temps en heures depuis 15:38
#t = tr.times() / 3600.0
#t = tr.times()
t = tr.times("matplotlib")

# =====================
# Subplot 1 : 8-15 Hz
# =====================
axes[0].plot(
    t, tr_HF.data,
    'k',
    linewidth=0.8
)

axes[0].set_ylabel("Amplitude (m/s)")
axes[0].set_title("Filtered 8-15 Hz")
axes[0].set_ylim([-4e-5, 4e-5])

# =====================
# Subplot 2 : VLP
# =====================
axes[1].plot(
    t, tr_VLP.data,
    'k',
    linewidth=0.8
)

axes[1].set_ylabel("Amplitude (m/s)")
axes[1].set_title("VLP 0.03-0.1 Hz")

# =====================
# Format des axes


#axes[-1].set_xlabel("Time since 15:38 UTC (hours)")
# Axe X : heures UTC
axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=1))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

axes[-1].set_xlim(ti.matplotlib_date, tf.matplotlib_date)
axes[-1].set_xlabel("Time (UTC)")

plt.tight_layout()
plt.show()

