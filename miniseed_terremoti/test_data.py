import numpy as np
from obspy import read


import numpy as np
from obspy import read

import numpy as np
from obspy import read

# Charger le fichier mseed
stream = read('/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed')
print(stream)
# Initialiser des listes pour stocker les données
stations = ['STR1', 'STR4', 'STRA', 'STRC', 'STRE', 'STRG']  # Noms des stations
composantes = ['EHZ', 'EHN', 'EHE']  # Composantes (EHE, EHN, EHZ)
data = np.zeros((18001, len(stations), len(composantes)))  # Matrice vide de données

# Parcourir les traces du fichier et remplir la matrice
for i, station in enumerate(stations):
    for j, comp in enumerate(composantes):
        # Trouver la trace correspondante à la station et à la composante
        trace = stream.select(station=f"IT.{station}..{comp}")[0]
        # Remplir la matrice avec les données
        data[:, i, j] = trace.data  # Remplir la colonne correspondante

# À ce stade, `data` est une matrice de forme (18001, 6, 3)
print(data.shape)