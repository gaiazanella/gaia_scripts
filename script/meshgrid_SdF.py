import numpy as np
import matplotlib.pyplot as plt

# Conversion des points en degrés décimaux
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),
}

# Extraire les limites
latitudes = [p[0] for p in points.values()]
longitudes = [p[1] for p in points.values()]

lat_min, lat_max = min(latitudes), max(latitudes)
lon_min, lon_max = min(longitudes), max(longitudes)

# Création de la grille
lat_grid = np.linspace(lat_min, lat_max, 100)
lon_grid = np.linspace(lon_min, lon_max, 100)
LAT, LON = np.meshgrid(lat_grid, lon_grid)

# Exemple de calcul pour une surface (vous pouvez utiliser des données réelles si disponibles)
# Ici, une fonction simple simulant une pente (juste pour visualisation)
Z = -(LAT - lat_min) - (LON - lon_min)  # Une pente simple pour illustration

# Visualisation
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(LON, LAT, Z, cmap='terrain')

# Labels et titres
ax.set_xlabel("Longitude (°E)")
ax.set_ylabel("Latitude (°N)")
ax.set_zlabel("Altitude (m)")
ax.set_title("Grille sur la Sciara del Fuoco (Stromboli)")

plt.show()
