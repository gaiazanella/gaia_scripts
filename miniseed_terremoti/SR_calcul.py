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
t_noise = UTCDateTime("2025-02-07T15:18:30")
#t_noise = UTCDateTime("2025-02-07T15:18:00")
dt = 30  # Recording duration in seconds
#dt=60*7

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
Pxx_noise_all_stations = {}
f_eq_all_stations = None
f_noise_all_stations = None

# Loop through the stations and retrieve waveforms for both periods
for station in stations:
    # Retrieve data for the "EQ" period
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    # Retrieve data for the "Noise" period
    sz_noise = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)

    # Get data for "EQ"
    data_eq = sz_eq[0].data
    # Apply detrend and demean to "EQ" data
    data_eq_detrended = detrend(data_eq)  # Remove the linear trend
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)  # Remove the mean

    # Get data for "Noise"
    data_noise = sz_noise[0].data
    # Apply detrend and demean to "Noise" data
    data_noise_detrended = detrend(data_noise)  # Remove the linear trend
    data_noise_demeaned = data_noise_detrended - np.mean(data_noise_detrended)  # Remove the mean

    # Sampling frequency
    fs = 100
    nperseg = len(data_eq)
    noverlap = 128
    
    # Compute the power spectral density for "EQ" (processed data)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Compute the power spectral density for "Noise" (processed data)
    f_noise, Pxx_noise = welch(data_noise_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Store the power spectral density for each station
    Pxx_eq_all_stations[station] = Pxx_eq
    Pxx_noise_all_stations[station] = Pxx_noise

    # Store the frequency arrays for the first station to align others
    if f_eq_all_stations is None:
        f_eq_all_stations = f_eq
        f_noise_all_stations = f_noise

    # Display amplitude as a function of frequency on a logarithmic scale for "EQ"
    plt.loglog(f_eq, smooth(Pxx_eq, 1), label=f"{station} - EQ", color=colors[station], linestyle='-', alpha=0.7)

    # Display amplitude as a function of frequency on a logarithmic scale for "Noise"
    plt.loglog(f_noise, smooth(Pxx_noise, 1), label=f"{station} - Noise", color=colors[station], linestyle='--', alpha=0.7)

# Figure settings
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Amplitude Spectrum using Welch's Method for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()


# Create a second figure for frequencies between 8 and 15 Hz
plt.figure(figsize=(8, 5))

# Filter and display spectra in the frequency range [8, 15] Hz
for station in stations:
    # Retrieve data for the "EQ" period
    sz_eq = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_eq, endtime=t_eq + dt)
    # Retrieve data for the "Noise" period
    sz_noise = client.get_waveforms(network="*", station=station, location="*", channel=channel, starttime=t_noise, endtime=t_noise + dt)

    # Get data for "EQ"
    data_eq = sz_eq[0].data
    # Apply detrend and demean to "EQ" data
    data_eq_detrended = detrend(data_eq)  # Remove the linear trend
    data_eq_demeaned = data_eq_detrended - np.mean(data_eq_detrended)  # Remove the mean

    # Get data for "Noise"
    data_noise = sz_noise[0].data
    # Apply detrend and demean to "Noise" data
    data_noise_detrended = detrend(data_noise)  # Remove the linear trend
    data_noise_demeaned = data_noise_detrended - np.mean(data_noise_detrended)  # Remove the mean

    # Sampling frequency
    fs = 100
    nperseg = len(data_eq)
    noverlap = 128

    # Compute the power spectral density for "EQ" (processed data)
    f_eq, Pxx_eq = welch(data_eq_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Compute the power spectral density for "Noise" (processed data)
    f_noise, Pxx_noise = welch(data_noise_demeaned * 1E-6 / 1200, fs=fs, nperseg=nperseg)

    # Filter frequencies and power spectral density for the [8, 15] Hz range
    idx_eq = (f_eq >= 8) & (f_eq <= 15)
    idx_noise = (f_noise >= 8) & (f_noise <= 15)

    # Display amplitude for frequencies between 8 and 15 Hz for "EQ"
    plt.loglog(f_eq[idx_eq], smooth(Pxx_eq[idx_eq], 1), label=f"{station} - EQ", color=colors[station], linestyle='-', alpha=0.7)

    # Display amplitude for frequencies between 8 and 15 Hz for "Noise"
    plt.loglog(f_noise[idx_noise], smooth(Pxx_noise[idx_noise], 1), label=f"{station} - Noise", color=colors[station], linestyle='--', alpha=0.7)

# Figure settings for the second figure
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Amplitude Spectrum (8-15 Hz) using Welch's Method for Different Stations (EQ vs Noise)")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()


# Ajouter à la fin de votre code après avoir calculé les spectres

# Créer une figure pour afficher les ratios spectraux
plt.figure(figsize=(8, 5))

# Station de référence
station_ref = 'STRA'

# Loop through the stations and calculate spectral ratio relative to station_ref (only for "EQ")
for station in stations:
    if station != station_ref:
        # Calculate the spectral ratio for "EQ" (station/STRA)
        ratio_eq = Pxx_eq_all_stations[station] / Pxx_eq_all_stations[station_ref]
        print(len(ratio_eq))

        # Display the spectral ratio for "EQ"
        plt.plot(f_eq, ratio_eq, label=f"{station} / {station_ref} - EQ", color=colors[station], linestyle='-', alpha=0.7)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Spectral Ratio")
plt.xscale('log')
#plt.title("Spectral Ratio (station / STRA) for Different Stations")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()

# Créer une figure pour afficher les ratios spectraux
plt.figure(figsize=(8, 5))

# Station de référence
station_ref = 'STRA'
print(Pxx_eq_all_stations)

# Boucle pour calculer et afficher les ratios spectraux pour chaque station (sauf la station de référence)
for station in stations:
    if station != station_ref:
        # Calcul du ratio spectral pour "EQ" (station/STRA)
        ratio_eq = Pxx_eq_all_stations[station] / Pxx_eq_all_stations[station_ref]
        ratio_eq=np.sqrt(ratio_eq)

        # Appliquer un lissage avec une fenêtre de 100 points
        ratio_eq_smoothed_10 = smooth(ratio_eq, 10)
        ratio_eq_smoothed_50 = smooth(ratio_eq, 50)
        ratio_eq_smoothed_5 = smooth(ratio_eq, 5)
        ratio_eq_smoothed_1 = smooth(ratio_eq, 1)
        ratio_eq_smoothed_100 = smooth(ratio_eq, 100)
        ratio_eq_smoothed_200 = smooth(ratio_eq, 200)
        ratio_eq_smoothed_1000 = smooth(ratio_eq, 1000)

        # Afficher le ratio spectral lissé pour chaque station
        #plt.plot(f_eq, ratio_eq_smoothed_100, label=f"{station} / {station_ref} - 100", linestyle='-')
        plt.plot(f_eq, ratio_eq_smoothed_1, label=f"{station} / {station_ref} - 1", linestyle='-')
        #plt.plot(f_eq, ratio_eq_smoothed_200, label=f"{station} / {station_ref} - 200", linestyle='-')
        #plt.plot(f_eq, ratio_eq_smoothed_10, label=f"{station} / {station_ref} - 10", linestyle='-')
        #plt.plot(f_eq, ratio_eq_smoothed_50, label=f"{station} / {station_ref} - 50", linestyle='-')
        #plt.plot(f_eq, ratio_eq_smoothed_5, label=f"{station} / {station_ref} - 5", linestyle='-')

plt.xlabel("Frequency (Hz)")
plt.xscale('log')
plt.ylabel("Ratio Spectral")
plt.title("Ratio Spectral")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()
