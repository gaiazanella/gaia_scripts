import rasterio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd

# Chemin vers ton fichier GeoTIFF et ton fichier CSV
data = "/home/gaia/Documents/SdF/test/test.tiff"
csv_file = "/home/gaia/Documents/MATLAB/SdF/frane_info_graph.csv"  # Remplace avec le chemin de ton fichier CSV

# Lire le fichier CSV pour obtenir les colonnes x0, y0, z0
df = pd.read_csv(csv_file, sep=';')  # Assurez-vous que le séparateur est bien ';' si c'est le cas

# Extraire les coordonnées des points
x0 = df['x0 longitude'].values
y0 = df['y0 latitude'].values
z0 = df['z0 elevation'].values

# Ouvrir le fichier GeoTIFF avec rasterio
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

    # Ajouter les points à la surface
    ax.scatter(x0, y0, z0, color='r', marker='o', s=50, label='Points (x0, y0, z0)')

    # Ajouter une barre de couleur
    fig.colorbar(ax.plot_surface(x, y, band1, cmap='viridis', rstride=1, cstride=1, edgecolor='none'))

    # Titres et labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Elevation')

    # Ajouter une légende
    ax.legend()

plt.tight_layout()
plt.show()
