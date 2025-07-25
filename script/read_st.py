### PACKAGES
from obspy import read, UTCDateTime
from scipy.signal import detrend, find_peaks
from obspy.signal.filter import bandpass, envelope
from obspy.core.trace import Trace
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import obspy.signal
from obspy.clients.filesystem.sds import Client
from obspy.signal.trigger import plot_trigger, classic_sta_lta
from datetime import datetime, timedelta
from scipy.stats import friedmanchisquare
#import seaborn as sns
import glob
import os

db = '/mnt/bigmama3'
stz = ['STRA', 'STRE','STRG', 'STR1', 'STR4', 'STR6']
net = ['IT', 'IV']
channel = ['EHE', '*HZ']
fs = 50  # Fréquence cible

client = Client(db)
ti = UTCDateTime("2025-06-06T00:00:00.000")
tf = ti + (60 * 60 * 24 * 1)

#st = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
st = client.get_waveforms(network='*', station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)
#st.plot()
st = client.get_waveforms(network='*', station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)

st = client.get_waveforms(network='*', station=stz[2], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)

st = client.get_waveforms(network='*', station=stz[3], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)

st = client.get_waveforms(network='*', station=stz[4], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)

st = client.get_waveforms(network='*', station=stz[5], location="", channel=channel[1], starttime=ti, endtime=tf)
print(st)

fff

st.merge(fill_value='interpolate')
st.detrend("demean")
st.detrend("linear")
data = st[0].data
data = bandpass(data, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

starttime = UTCDateTime(st[0].stats.starttime).datetime
time = pd.to_datetime(starttime + pd.to_timedelta(np.arange(0, len(data) / fs, 1 / fs), unit='s'))


plt.figure(figsize=(12, 6))

plt.plot(time, data)

#st.plot()
plt.show()