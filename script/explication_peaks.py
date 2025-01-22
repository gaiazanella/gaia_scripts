import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Générer un signal ECG simulé avec des valeurs aléatoires
np.random.seed(42)  # Pour assurer la reproductibilité
t = np.linspace(0, 10, 100)  # Temps de 0 à 10 secondes avec 10000 points
ecg_signal = 0.5 * np.sin(2 * np.pi * 1 * t) + 0.3 * np.random.randn(t.size)  # Signal sinusoidal avec du bruit

# Ajouter des pics "simulés" pour ressembler à des complexes R
ecg_signal[1000:1020] += 2  # Un pic "R" à une position donnée
ecg_signal[3000:3020] += 2  # Un autre pic "R"
ecg_signal[5000:5020] += 2  # Un autre pic "R"
ecg_signal[7000:7020] += 2  # Un autre pic "R"

# Zoomer sur une portion de 10000 données entre 400 et 800 (pour simplification)
x_zoom = ecg_signal

# Trouver les pics et leurs propriétés
peaks, properties = find_peaks(x_zoom, prominence=0.5,wlen=5)
prominences = properties["prominences"]

# Calculer la position des barres horizontales à la moitié de la proéminence
half_prominence_heights = x_zoom[peaks] - prominences / 2

# Tracer la partie zoomée du signal
plt.figure(figsize=(10, 6))
plt.plot(x_zoom, label="ECG signal (zoomed in)")
plt.plot(peaks, x_zoom[peaks], "x", label="Peaks detected")
plt.vlines(x=peaks, ymin=x_zoom[peaks] - prominences,
           ymax=x_zoom[peaks], color="C1", label="Prominence")
#plt.hlines(y=half_prominence_heights, xmin=properties["left_ips"],
#           xmax=properties["right_ips"], color="C1", label="Width heights")
plt.legend()
plt.title('Zoomed In: Simulated ECG Signal with Peak Detection')
plt.xlabel('Time Index')
plt.ylabel('Signal Amplitude')
plt.grid(True)
plt.show()
