from obspy import read
import matplotlib.pyplot as plt
import numpy as np

# Charger les données sismiques
stream = read("/home/gaia/Documents/mseed_terremoti/20240801_M5.1.mseed")
print(stream)
trace = stream[8] 
print(trace)

stream.detrend("demean") #met le signal autour de zéro 
stream.detrend("linear") 
win = 30 #60 #window of 60 seconds, 1 min

sampling_rate = trace.stats.sampling_rate
samples = int(win * sampling_rate)

window = np.ones(samples) / samples # crée un tableau rempli de 1 de taille égale à window_size ; chaque case devient 1/window_size : moyenne uniforme
smoothed_signal = np.convolve(trace.data, window, mode='same')

print(trace)

# Prétraitement
#trace.detrend(type='linear')  # Retirer une tendance linéaire
#trace.taper(0.05)  # Appliquer une fenêtre de Hanning (5% de chaque côté)

# Récupérer les données de la trace
data = trace.data
print(data)
data=data*3.18**(-6)/800 ## STRA
#data=data*1.00**(-6)/1200 ## STRC
#data=data*3.20**(-6)/800 ## STRE
#data=data*1.00**(-6)/1200 ## STRG
print(data)
print(len (data))

# Calcul de la FFT
n = len(data)
frequencies = np.fft.fftfreq(n, d=1/sampling_rate)  # Fréquences en Hz
print(frequencies)
print (len (frequencies))
### crée un vecteur des fréquences correspondant à chaque échantillon du spectre

#frequencies = np.fft.fftshift(frequencies)  
# Déplacer zéro fréquence au centre
print(frequencies)

# Appliquer FFT et obtenir l'amplitude
spectrum = np.fft.fft(data)
print(spectrum)
print(len(spectrum))
## calcule la FFT du signal temporel data. 
## Le résultat es un tableau complexe où chaque élément contient unue amplitude et une phase pour una fréquence particuelière

#spectrum = np.fft.fftshift(spectrum)  # Déplacer zéro fréquence au centre
print(spectrum)

amplitudes = np.abs(spectrum)  # Amplitude du spectre
## extrait l'amplitude de chaque composant fréquentiel (car la fft retourne des nombrers complexes, et tu veux les magnitudes)
print(amplitudes)
print(len(amplitudes))

# Filtrer les fréquences négatives
positive_frequencies = frequencies[frequencies > 0]
positive_amplitudes = amplitudes[frequencies > 0]

# Affichage du spectre
plt.figure(figsize=(10, 6))
plt.plot(positive_frequencies, positive_amplitudes)
plt.title("Spectre des données sismiques")
plt.xlabel("Fréquence (Hz)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()
