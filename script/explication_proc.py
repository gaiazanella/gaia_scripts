import obspy
from obspy import UTCDateTime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy.clients.filesystem.sds import Client
from obspy.signal.filter import bandpass, envelope
from datetime import timedelta

# Function to smooth a signal
def smooth(signal, window_size):
    window = np.ones(window_size) / window_size
    smoothed_signal = np.convolve(signal, window, mode='same')
    return smoothed_signal

# Parameters
win = 60  # Window size in seconds
fs = 50  # Sampling frequency
samples = win * fs
t_init = UTCDateTime("2020-10-11T02:20:00")
t_end = UTCDateTime("2020-10-11T02:40:00")  # 1 hour of data
db = '/mnt/bigmama3/miniseed'
stz = 'STRA'  # Single station for simplicity
net = 'IT'
channel = '*HZ'
fminb3, fmaxb3 = 1, 8
fminb4, fmaxb4 = 8, 15

client = Client(db)

# Retrieve waveform
st = client.get_waveforms(network=net, station=stz, location="", channel=channel, starttime=t_init, endtime=t_end)
st.merge(fill_value='interpolate')
st.detrend("demean")
st.detrend("linear")

# Process for both frequency bands
st_b3 = st.copy().filter('bandpass', freqmin=fminb3, freqmax=fmaxb3)
st_b4 = st.copy().filter('bandpass', freqmin=fminb4, freqmax=fmaxb4)

# Envelope and smoothing
s_env_b3 = envelope(st_b3[0].data)
s_env_b4 = envelope(st_b4[0].data)
s_env_smooth_b3 = smooth(s_env_b3, samples)
s_env_smooth_b4 = smooth(s_env_b4, samples)

# Generate time axis
time = pd.to_datetime(t_init.datetime + pd.to_timedelta(np.arange(0, len(st[0].data) / fs, 1 / fs), unit='S'))

# Visualization
plt.figure(figsize=(12, 8))
plt.plot(time, st[0].data, label='Raw Signal', color='gray', alpha=0.7)
plt.plot(time, st_b3[0].data, label='Filtered 1-8 Hz', color='blue')
#plt.plot(time, st_b4[0].data, label='Filtered 8-15 Hz', color='green')
plt.plot(time, s_env_b3, label='Envelope 1-8 Hz', color='cyan', linestyle='dotted')
#plt.plot(time, s_env_b4, label='Envelope 8-15 Hz', color='lime', linestyle='dotted')
plt.plot(time, s_env_smooth_b3, label='Smoothed Envelope 1-8 Hz', color='navy', linestyle='dashed')
#plt.plot(time, s_env_smooth_b4, label='Smoothed Envelope 8-15 Hz', color='darkgreen', linestyle='dashed')

# Formatting
plt.xlabel("Time (UTC)")
plt.ylabel("RSAM (counts)")
plt.title(f"Signal Processing Steps for Station {stz}")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()
