import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.misc import electrocardiogram  # Pour le signal électrocardiogramme

# Charger un signal d'électrocardiogramme et en extraire une partie
x = electrocardiogram()[17000:18000]

# Trouver les pics et leurs propriétés
peaks, properties = find_peaks(x, prominence=1, width=5)

# Afficher les propriétés des pics
print("Prominences:", properties["prominences"])
print("Widths:", properties["widths"])

# Tracer le signal et marquer les pics
plt.plot(x, label="Signal ECG")  # Tracer le signal ECG
plt.plot(peaks, x[peaks], "x", label="Peaks")  # Marquer les pics avec des croix
plt.vlines(
    x=peaks,
    ymin=x[peaks] - properties["prominences"],
    ymax=x[peaks],
    color="C1",
    label="Prominence",
)  # Lignes verticales pour les prominences
plt.hlines(
    y=properties["width_heights"],
    xmin=properties["left_ips"],
    xmax=properties["right_ips"],
    color="C1",
    label="Width",
)  # Lignes horizontales pour les largeurs
plt.legend()
plt.show()
