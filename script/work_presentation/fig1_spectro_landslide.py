import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Parameters
db = '/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']
fs = 50  # Target frequency

# Client to retrieve data
client = Client(db)
ti = UTCDateTime("2020-10-07T02:55:30.000")
tf = ti + (60 * 2.5 * 1 * 1)  # 2.5 minutes of data

# Retrieve data for both stations
sta = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[1], starttime=ti, endtime=tf)
ste = client.get_waveforms(network=net[1], station=stz[1], location="", channel=channel[1], starttime=ti, endtime=tf)

# Merge data (interpolation)
sta.merge(fill_value='interpolate')
ste.merge(fill_value='interpolate')

# Detrend the signals
sta.detrend("demean")
sta.detrend("linear")
ste.detrend("demean")
ste.detrend("linear")

# Apply bandpass filter to the data
dataa = sta[0].data
datae = ste[0].data
dataa = dataa * ((3.2 * 10**(-6)) / 800)
datae = datae * ((3.2 * 10**(-6)) / 800)
dataa1 = bandpass(dataa, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)
datae1 = bandpass(datae, freqmin=0.03, freqmax=24, df=fs, corners=4, zerophase=True)

# Convert timestamps to datetime
starttimea = UTCDateTime(sta[0].stats.starttime).datetime
starttimee = UTCDateTime(ste[0].stats.starttime).datetime
timea = pd.to_datetime(starttimea + pd.to_timedelta(np.arange(0, len(dataa) / fs, 1 / fs), unit='s'))
timee = pd.to_datetime(starttimee + pd.to_timedelta(np.arange(0, len(datae) / fs, 1 / fs), unit='s'))

# Extract first trace (if multiple traces are retrieved)
trace = sta[0]

# Access signal data
signal = trace.data

# Check sampling frequency
fs = trace.stats.sampling_rate
print(f"Sampling frequency: {fs} Hz")

# Compute the spectrogram
f, t_spec, Sxx = spectrogram(signal, fs)

# Plot the spectrogram
plt.figure(figsize=(10, 6))
plt.pcolormesh(t_spec, f, 10 * np.log10(Sxx), shading='auto')

# Zoom in on frequencies between 0 and 24 Hz
plt.ylim(0, 24)  # Limit frequency axis to 0-24 Hz

# Add labels and title in English
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [s]')
plt.colorbar(label='Power [dB]')
plt.title('Seismic Trace Spectrogram')

# Show the plot
plt.show()
