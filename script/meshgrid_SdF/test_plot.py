import rasterio
import matplotlib.pyplot as plt
import rasterio.plot

# Chemin vers ton fichier GeoTIFF
data = "/home/gaia/Documents/SdF/test/test.tiff"

# Ouvrir le fichier original
with rasterio.open(data) as src:
    band1 = src.read(1)  # Lire la première bande du raster

    # Afficher l'image originale
    plt.figure(figsize=(12, 6))
    plt.imshow(band1, cmap='viridis')
    plt.colorbar()  # Ajouter une barre de couleur pour l'image originale

plt.tight_layout()
plt.show()  # Afficher les deux images côte à côte

import rasterio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Chemin vers ton fichier GeoTIFF
data = "/home/gaia/Documents/SdF/test/test.tif"

with rasterio.open(data) as src:
    band1 = src.read(1)  # Lire la première bande du raster

    # Créer une figure et une ax pour l'affichage en 3D
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Créer une grille de coordonnées (x, y) correspondant aux dimensions du raster
    x = np.arange(band1.shape[1])
    y = np.arange(band1.shape[0])
    x, y = np.meshgrid(x, y)

    # Afficher la surface en 3D (avec l'élévation comme couleur)
    ax.plot_surface(x, y, band1, cmap='viridis', rstride=1, cstride=1, edgecolor='none')

    # Ajouter une barre de couleur
    fig.colorbar(ax.plot_surface(x, y, band1, cmap='viridis', rstride=1, cstride=1, edgecolor='none'))

    # Titres et labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Elevation')

plt.tight_layout()
plt.show()
