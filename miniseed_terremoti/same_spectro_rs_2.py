from obspy.clients.filesystem.sds import Client
from obspy import UTCDateTime
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend  # Correct import of detrend
import numpy as np
from obspy.signal.util import smooth  # Import smooth from obspy.signal.util

# Initialize the client for the SDS directory
client = Client("/mnt/bigmama3")

# Start time
t_eq = UTCDateTime("2025-02-07T15:19:30")
#t_eq = UTCDateTime("2025-02-07T15:18:00")

#t_noise = UTCDateTime("2025-02-07T15:18:00")
#dt = 30  # Recording duration in seconds
dt=60*7

# Stations and channels to retrieve
stations = ['STRA', 'STRC', 'STRE', 'STRG']
channel = '*HZ'  # The channel to retrieve (all horizontal channels)

# Dictionary to assign specific colors to each station
colors = {
    'STRA': 'red',   # STRA in red
    'STRC': 'cyan',  # STRC in cyan
    'STRE': 'blue',  # STRE in blue
    'STRG': 'magenta' # STRG in magenta
}

# Create a figure for the display
plt.figure(figsize=(8, 5))

# Dictionary to store the spectra for each station
Pxx_eq_all_stations = {}
f_eq_all_stations = None

# Loop through the stations and retrieve waveforms for both periods
for station in stations:
    # Retrieve data for the "EQ" period
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    
    # Get data for "EQ"
    data_eq = sz_eq[0].data
    # Apply detrend and demean to "EQ" data
    data_eq_detrended = detrend(data_eq)  # Remove the linear trend
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)  # Remove the mean

    # Sampling frequency
    fs = 100
    nperseg = len(data_eq)
    noverlap = 128
    
    # Compute the power spectral density for "EQ" (processed data)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)


    Pxx_eq_all_stations[station] = Pxx_eq

    # Store the frequency arrays for the first station to align others
    if f_eq_all_stations is None:
        f_eq_all_stations = f_eq

    # Display amplitude as a function of frequency on a logarithmic scale for "EQ"
    plt.loglog(f_eq, Pxx_eq, label=f"{station}", color=colors[station], linestyle='-', alpha=0.7)

   
# Figure settings
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
#plt.title("Amplitude Spectrum using Welch's Method for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()