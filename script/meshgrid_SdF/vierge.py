import rasterio
import numpy as np

dataset = rasterio.open('/home/gaia/Documents/SdF/vierge.tiff')

print(dataset.name)
print(dataset.mode)

print(dataset.closed)

print(dataset.count)

print(dataset.bounds)

print(dataset.transform)

print(dataset.transform * (0, 0))

print(dataset.shape)

# Définir les deux valeurs et le nombre de points
valeur_initiale_long = 38.758194444
valeur_finale_long = 38.820972222
nombre_points_long = 226

# Créer le vecteur
long = np.linspace(valeur_initiale_long, valeur_finale_long, nombre_points_long)

# Afficher le vecteur
print(long)

# Définir les deux valeurs et le nombre de points
valeur_initiale_lat = 15.166527778
valeur_finale_lat = 15.262638889
nombre_points_lat = 346

# Créer le vecteur
long = np.linspace(valeur_initiale_long, valeur_finale_long, nombre_points_lat)

# Afficher le vecteur
print(long)

new_dataset = rasterio.open('/home/gaia/Documents/SdF/vierge.tiff','w')