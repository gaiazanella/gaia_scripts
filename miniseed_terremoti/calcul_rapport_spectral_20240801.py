from obspy import read
import numpy as np
import matplotlib.pyplot as plt

# Charger les données sismiques des deux stations
stream_station = read("/home/gaia/Documents/mseed_terremoti/20240801_M5.1.mseed")
stream_station.detrend("demean") #met le signal autour de zéro 
stream_station.detrend("linear") 

win = 30 #60 #window of 60 seconds, 1 min

# Choisir la trace de chaque station (par exemple, la première trace de chaque stream)
trace_station_stra = stream_station[10]
trace_station_stre = stream_station[17]
trace_station_strc = stream_station[13]
trace_station_strg = stream_station[21]

sampling_rate = trace_station_stra.stats.sampling_rate
samples = int(win * sampling_rate)

window = np.ones(samples) / samples # crée un tableau rempli de 1 de taille égale à window_size ; chaque case devient 1/window_size : moyenne uniforme
smoothed_signal_stra = np.convolve(trace_station_stra.data, window, mode='same')
smoothed_signal_stre = np.convolve(trace_station_stre.data, window, mode='same')
smoothed_signal_strc = np.convolve(trace_station_strg.data, window, mode='same')
smoothed_signal_strg = np.convolve(trace_station_strg.data, window, mode='same')

# Récupérer les données de chaque station
data_station_stra = trace_station_stra.data
data_station_stre = trace_station_stre.data
data_station_strc = trace_station_strc.data
data_station_strg = trace_station_strg.data
data_station_stra=data_station_stra*3.18**(-6)/800 ## STRA
data_station_strc=data_station_strc*1.00**(-6)/1200 ## STRC
data_station_stre=data_station_stre*3.20**(-6)/800 ## STRE
data_station_strg=data_station_strg*1.00**(-6)/1200 ## STRG


# Calcul de la FFT pour chaque station
spectrum_station_stra = np.fft.fft(data_station_stra)
spectrum_station_stre = np.fft.fft(data_station_stre)
spectrum_station_strc = np.fft.fft(data_station_strc)
spectrum_station_strg = np.fft.fft(data_station_strg)

# Calcul des amplitudes spectrales
amplitude_station_stra = np.abs(spectrum_station_stra)
amplitude_station_stre = np.abs(spectrum_station_stre)
amplitude_station_strc = np.abs(spectrum_station_strc)
amplitude_station_strg = np.abs(spectrum_station_strg)

# Calcul des fréquences associées
n = len(data_station_stra)
frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

# Ne garder que les fréquences positives
positive_frequencies = frequencies[frequencies > 0]
#useful_frequencies = positive_frequencies[(positive_frequencies > 8) & (positive_frequencies < 15)]
amplitude_station_stra = amplitude_station_stra[frequencies > 0]
amplitude_station_stre = amplitude_station_stre[frequencies > 0]
amplitude_station_strc = amplitude_station_strc[frequencies > 0]
amplitude_station_strg = amplitude_station_strg[frequencies > 0]

amplitude_station_ref = amplitude_station_stra

# Calcul du rapport spectral (station 1 / station 2)
spectral_ratio_e = amplitude_station_stre / amplitude_station_ref
spectral_ratio_c = amplitude_station_strc / amplitude_station_ref
spectral_ratio_g = amplitude_station_strg / amplitude_station_ref
#print(spectral_ratio)

# Calculer le spectrogramme avec plt.specgram
plt.figure(figsize=(10, 6))
plt.specgram(data_station_stra, NFFT=256, Fs=sampling_rate, noverlap=128, scale='dB', cmap='inferno')
plt.title("Spectrogramme STRA")
plt.xlabel("Time (s)")
plt.ylabel("Freq (Hz)")
plt.colorbar(label="Amplitude (dB)")
plt.show()

# Calculer le spectrogramme avec plt.specgram
plt.figure(figsize=(10, 6))
plt.specgram(data_station_stre, NFFT=256, Fs=sampling_rate, noverlap=128, scale='dB', cmap='inferno')
plt.title("Spectrogramme STRE")
plt.xlabel("Time (s)")
plt.ylabel("Freq (Hz)")
plt.colorbar(label="Amplitude (dB)")
plt.show()

# Calculer le spectrogramme avec plt.specgram
plt.figure(figsize=(10, 6))
plt.specgram(data_station_strc, NFFT=256, Fs=sampling_rate, noverlap=128, scale='dB', cmap='inferno')
plt.title("Spectrogramme STRC")
plt.xlabel("Time (s)")
plt.ylabel("Freq (Hz)")
plt.colorbar(label="Amplitude (dB)")
plt.show()

# Calculer le spectrogramme avec plt.specgram
plt.figure(figsize=(10, 6))
plt.specgram(data_station_strg, NFFT=256, Fs=sampling_rate, noverlap=128, scale='dB', cmap='inferno')
plt.title("Spectrogramme STRG")
plt.xlabel("Time (s)")
plt.ylabel("Freq (Hz)")
plt.colorbar(label="Amplitude (dB)")
plt.show()
fff

# Affichage du rapport spectral
plt.figure(figsize=(10, 6))
plt.plot(positive_frequencies, spectral_ratio_e, color='blue', label='STRE/STRA')
plt.plot(positive_frequencies, spectral_ratio_c, color='black', label='STRC/STRA')
plt.plot(positive_frequencies, spectral_ratio_g, color='magenta', label='STRG/STRA')
plt.title("2024-08-01 T19:43:20")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Spectral Ratio")
plt.legend()
plt.grid(True)
plt.show()
