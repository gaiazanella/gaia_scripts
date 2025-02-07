from obspy import read
import numpy as np
import matplotlib.pyplot as plt

# Charger les données sismiques des deux stations
stream_station = read("/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed")
stream_station.detrend("demean") #met le signal autour de zéro 
stream_station.detrend("linear") 
print(stream_station)

win = 30 #30sec

trace_station_stra = stream_station[8]
print(trace_station_stra)
trace_station_stre = stream_station[14]
print(trace_station_stre)
trace_station_strc = stream_station[11]
print(trace_station_strc)
trace_station_strg = stream_station[17]
print(trace_station_strg)

sampling_rate = trace_station_stra.stats.sampling_rate
samples = int(win * sampling_rate)

window = np.ones(samples) / samples 
smoothed_signal_stra = np.convolve(trace_station_stra.data, window, mode='same')
smoothed_signal_stre = np.convolve(trace_station_stre.data, window, mode='same')
smoothed_signal_strc = np.convolve(trace_station_strc.data, window, mode='same')
smoothed_signal_strg = np.convolve(trace_station_strg.data, window, mode='same')

# data station
data_station_stra = trace_station_stra.data
data_station_stre = trace_station_stre.data
data_station_strc = trace_station_strc.data
data_station_strg = trace_station_strg.data
data_station_stra=data_station_stra*3.18**(-6)/800 ## STRA
data_station_strc=data_station_strc*1.00**(-6)/1200 ## STRC
data_station_stre=data_station_stre*3.20**(-6)/800 ## STRE
data_station_strg=data_station_strg*1.00**(-6)/1200 ## STRG

# FFT calcul for each station
spectrum_station_stra = np.fft.fft(data_station_stra)
spectrum_station_stre = np.fft.fft(data_station_stre)
spectrum_station_strc = np.fft.fft(data_station_strc)
spectrum_station_strg = np.fft.fft(data_station_strg)

# Spectral amplitude calcul for each station
amplitude_station_stra = np.abs(spectrum_station_stra)
amplitude_station_stre = np.abs(spectrum_station_stre)
amplitude_station_strc = np.abs(spectrum_station_strc)
amplitude_station_strg = np.abs(spectrum_station_strg)

# frequencies associated calcul
n = len(data_station_stra)
frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

# keep positive frequencies
positive_frequencies = frequencies[frequencies > 0]
amplitude_station_stra = amplitude_station_stra[frequencies > 0]
amplitude_station_stre = amplitude_station_stre[frequencies > 0]
amplitude_station_strc = amplitude_station_strc[frequencies > 0]
amplitude_station_strg = amplitude_station_strg[frequencies > 0]

amplitude_station_ref = amplitude_station_strg

# ratio spectral calcul
spectral_ratio_e = amplitude_station_stre / amplitude_station_ref
spectral_ratio_c = amplitude_station_strc / amplitude_station_ref
spectral_ratio_g = amplitude_station_strg / amplitude_station_ref
spectral_ratio_a = amplitude_station_stra / amplitude_station_ref

# Affichage du rapport spectral
plt.figure(figsize=(10, 6))
plt.plot(positive_frequencies, spectral_ratio_e, color='blue', label='STRE/STRG')
plt.plot(positive_frequencies, spectral_ratio_c, color='black', label='STRC/STRG')
plt.plot(positive_frequencies, spectral_ratio_a, color='red', label='STRA/STRG')
plt.title("2020-10-21 T23:00:54, Ref station STRG")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Spectral Ratio")
plt.legend()
plt.grid(True)
plt.show()

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

# Affichage du spectre de chaque station
plt.figure(figsize=(10, 6))
#plt.plot(positive_frequencies, amplitude_station_stra, label='STRA', color='red')
#plt.plot(positive_frequencies, amplitude_station_stre, label='STRE', color='blue')
#plt.plot(positive_frequencies, amplitude_station_strc, label='STRC', color='black')
plt.plot(positive_frequencies, amplitude_station_strg, label='STRG', color='magenta')
plt.title("Spectre STRG")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()

# Affichage du spectre de chaque station
plt.figure(figsize=(10, 6))
#plt.plot(positive_frequencies, amplitude_station_stra, label='STRA', color='red')
#plt.plot(positive_frequencies, amplitude_station_stre, label='STRE', color='blue')
plt.plot(positive_frequencies, amplitude_station_strc, label='STRC', color='black')
#plt.plot(positive_frequencies, amplitude_station_strg, label='STRG', color='magenta')
plt.title("Spectres des stations")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()

# Affichage du spectre de chaque station
plt.figure(figsize=(10, 6))
#plt.plot(positive_frequencies, amplitude_station_stra, label='STRA', color='red')
plt.plot(positive_frequencies, amplitude_station_stre, label='STRE', color='blue')
#plt.plot(positive_frequencies, amplitude_station_strc, label='STRC', color='black')
#plt.plot(positive_frequencies, amplitude_station_strg, label='STRG', color='magenta')
plt.title("Spectre STRE")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()

# Affichage du spectre de chaque station
plt.figure(figsize=(10, 6))
plt.plot(positive_frequencies, amplitude_station_stra, label='STRA', color='red')
#plt.plot(positive_frequencies, amplitude_station_stre, label='STRE', color='blue')
#plt.plot(positive_frequencies, amplitude_station_strc, label='STRC', color='black')
#plt.plot(positive_frequencies, amplitude_station_strg, label='STRG', color='magenta')
plt.title("Spectre STRA")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()