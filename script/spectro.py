import matplotlib.pyplot as plt
import numpy as np

# Exemple : Signal synthétique avec deux fréquences
fs = 100  # Fréquence d'échantillonnage (Hz)
t = np.linspace(0, 10, fs*10)  # 10 secondes
signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)  # 5 Hz et 20 Hz

# Calcul du spectrogramme
Pxx, freqs, bins, im = plt.specgram(signal, NFFT=128, Fs=fs, noverlap=64, cmap='viridis')

# Ajout de labels
plt.title("Spectrogramme")
plt.xlabel("Temps (s)")
plt.ylabel("Fréquence (Hz)")
plt.colorbar(label="Amplitude (dB)")

# Afficher le spectrogramme
plt.show()
