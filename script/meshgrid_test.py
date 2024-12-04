import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Coordonnées des points A, B, C, D
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),  # Vers la mer
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),  # Vers la mer
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),  # Vers le sommet
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),  # Vers le sommet
}

# Créer une carte avec une projection Plate Carrée
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Étendre les limites géographiques pour voir toute la zone autour des points A, B, C, D
ax.set_extent([15.17, 15.26, 38.75, 38.82], crs=ccrs.PlateCarree())  # Ajuster l'étendue pour mieux voir la région

# Ajouter des caractéristiques géographiques de base
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')

# Tracer les lignes entre les points A, B, C, D
lons, lats = zip(*[points["A"], points["C"], points["D"], points["B"], points["A"]])  # Ajouter A à la fin pour fermer le polygone

# Tracer les lignes en bleu avec un large trait pour plus de visibilité
ax.plot(lons, lats, marker='o', color='blue', markersize=8, label="Sciara del Fuoco", transform=ccrs.PlateCarree(), linewidth=2)

# Ajouter les points de façon annotée
for point, (lat, lon) in points.items():
    ax.text(lon, lat, f"{point}", transform=ccrs.PlateCarree(), fontsize=12, color='red', weight='bold', ha='center')

# Ajouter un titre
plt.title("Carte de la Sciara del Fuoco sur Stromboli", fontsize=16)

# Afficher la carte avec la légende
plt.legend(loc='lower right')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Coordonnées des points A, B, C, D
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),  # Vers la mer
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),  # Vers la mer
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),  # Vers le sommet
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),  # Vers le sommet
}

# Extraire les coordonnées minimales et maximales pour la grille
lons = [lon for _, lon in points.values()]
lats = [lat for lat, _ in points.values()]

lon_min, lon_max = min(lons), max(lons)
lat_min, lat_max = min(lats), max(lats)

# Calculer les espacements en degrés pour 10 mètres
# 1° de latitude = 111,000 mètres, donc l'espacement de 10m correspond à (10 / 111,000) degrés
lat_spacing = 10 / 111000  # Espacement en degrés pour la latitude (10 mètres)
# Calculer la distance en degrés pour la longitude à la latitude moyenne
avg_lat = np.mean([lat_min, lat_max])  # Latitude moyenne
lon_spacing = 10 / (111000 * np.cos(np.radians(avg_lat)))  # Espacement en degrés pour la longitude (10 mètres)

# Créer une grille de points entre les limites avec un espacement de 10m
lon_grid, lat_grid = np.meshgrid(np.arange(lon_min, lon_max, lon_spacing),
                                 np.arange(lat_min, lat_max, lat_spacing))

# Exemple de fonction pour calculer des valeurs sur la grille (ici une simple fonction)
# Par exemple, calculons une valeur basée sur la distance entre chaque point et un des points de la Sciara del Fuoco
def example_function(lons, lats, center_lon=points["A"][1], center_lat=points["A"][0]):
    # Calcul de la distance à partir du centre (ex: point A)
    return np.sqrt((lons - center_lon) ** 2 + (lats - center_lat) ** 2)

# Calcul des valeurs pour chaque point de la grille
values = example_function(lon_grid, lat_grid)

# Créer une carte avec une projection Plate Carrée
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Étendre les limites géographiques pour voir toute la zone autour des points A, B, C, D
ax.set_extent([lon_min - 0.01, lon_max + 0.01, lat_min - 0.01, lat_max + 0.01], crs=ccrs.PlateCarree())  # Ajuster l'étendue pour mieux voir la région

# Ajouter des caractéristiques géographiques de base
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')

# Tracer les lignes entre les points A, B, C, D
lons, lats = zip(*[points["A"], points["C"], points["D"], points["B"], points["A"]])  # Ajouter A à la fin pour fermer le polygone
ax.plot(lons, lats, marker='o', color='blue', markersize=8, label="Sciara del Fuoco", transform=ccrs.PlateCarree(), linewidth=2)

# Ajouter les points de façon annotée
for point, (lat, lon) in points.items():
    ax.text(lon, lat, f"{point}", transform=ccrs.PlateCarree(), fontsize=12, color='red', weight='bold', ha='center')

# Tracer les contours de la grille de valeurs
# Par exemple, tracons des lignes de niveau pour afficher des différences de valeurs
contour = ax.contour(lon_grid, lat_grid, values, 10, transform=ccrs.PlateCarree(), cmap='coolwarm')

# Ajouter un titre
plt.title("Carte de la Sciara del Fuoco avec Meshgrid Espacée de 10 mètres", fontsize=16)

# Afficher la légende pour les contours
plt.colorbar(contour, ax=ax, orientation="vertical", label="Valeurs calculées")

# Afficher la carte avec la légende
plt.legend(loc='lower right')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Coordonnées des points A, B, C, D, STRA et STRE
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),  # Vers la mer
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),  # Vers la mer
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),  # Vers le sommet
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),  # Vers le sommet
    "STRA": (38 + 47/60 + 42/3600, 15 + 13/60 + 1/3600),  # Point STRA
    "STRE": (38 + 48/60 + 8/3600, 15 + 12/60 + 54/3600),  # Point STRE
}

# Extraire les coordonnées minimales et maximales pour la grille
lons = [lon for _, lon in points.values()]
lats = [lat for lat, _ in points.values()]

lon_min, lon_max = min(lons), max(lons)
lat_min, lat_max = min(lats), max(lats)

# Calculer les espacements en degrés pour 10 mètres
lat_spacing = 10 / 111000  # Espacement en degrés pour la latitude (10 mètres)
avg_lat = np.mean([lat_min, lat_max])  # Latitude moyenne
lon_spacing = 10 / (111000 * np.cos(np.radians(avg_lat)))  # Espacement en degrés pour la longitude (10 mètres)

# Créer une grille de points entre les limites avec un espacement de 10m
lon_grid, lat_grid = np.meshgrid(np.arange(lon_min, lon_max, lon_spacing),
                                 np.arange(lat_min, lat_max, lat_spacing))

# Exemple de fonction pour calculer des valeurs sur la grille (ici une simple fonction)
def example_function(lons, lats, center_lon=points["A"][1], center_lat=points["A"][0]):
    # Calcul de la distance à partir du centre (ex: point A)
    return np.sqrt((lons - center_lon) ** 2 + (lats - center_lat) ** 2)

# Calcul des valeurs pour chaque point de la grille
values = example_function(lon_grid, lat_grid)

# Créer une carte avec une projection Plate Carrée
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Étendre les limites géographiques pour voir toute la zone autour des points A, B, C, D, STRA et STRE
ax.set_extent([lon_min - 0.01, lon_max + 0.01, lat_min - 0.01, lat_max + 0.01], crs=ccrs.PlateCarree())  # Ajuster l'étendue pour mieux voir la région

# Ajouter des caractéristiques géographiques de base
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')

# Tracer les lignes entre les points A, B, C, D
lons, lats = zip(*[points["A"], points["C"], points["D"], points["B"], points["A"]])  # Ajouter A à la fin pour fermer le polygone
ax.plot(lons, lats, marker='o', color='blue', markersize=8, label="Sciara del Fuoco", transform=ccrs.PlateCarree(), linewidth=2)

# Ajouter les points de façon annotée
for point, (lat, lon) in points.items():
    ax.text(lon, lat, f"{point}", transform=ccrs.PlateCarree(), fontsize=12, color='red', weight='bold', ha='center')

# Tracer les contours de la grille de valeurs
contour = ax.contour(lon_grid, lat_grid, values, 10, transform=ccrs.PlateCarree(), cmap='coolwarm')

# Ajouter un titre
plt.title("Carte de la Sciara del Fuoco avec Meshgrid Espacée de 10 mètres", fontsize=16)

# Afficher la légende pour les contours
plt.colorbar(contour, ax=ax, orientation="vertical", label="Valeurs calculées")

# Afficher la carte avec la légende
plt.legend(loc='lower right')
plt.show()


import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Coordonnées des points A, B, C, D, STRA et STRE
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),  # Vers la mer
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),  # Vers la mer
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),  # Vers le sommet
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),  # Vers le sommet
    "STRA": (38 + 47/60 + 42/3600, 15 + 13/60 + 1/3600),  # Point STRA
    "STRE": (38 + 48/60 + 8/3600, 15 + 12/60 + 54/3600),  # Point STRE
}

# Extraire les coordonnées minimales et maximales pour la grille
lons = [lon for _, lon in points.values()]
lats = [lat for lat, _ in points.values()]

lon_min, lon_max = min(lons), max(lons)
lat_min, lat_max = min(lats), max(lats)

# Calculer les espacements en degrés pour 10 mètres
lat_spacing = 10 / 111000  # Espacement en degrés pour la latitude (10 mètres)
avg_lat = np.mean([lat_min, lat_max])  # Latitude moyenne
lon_spacing = 10 / (111000 * np.cos(np.radians(avg_lat)))  # Espacement en degrés pour la longitude (10 mètres)

# Créer une grille de points entre les limites avec un espacement de 10m
lon_grid, lat_grid = np.meshgrid(np.arange(lon_min, lon_max, lon_spacing),
                                 np.arange(lat_min, lat_max, lat_spacing))

# Exemple de fonction pour calculer des valeurs sur la grille (ici une simple fonction)
def example_function(lons, lats, center_lon=points["A"][1], center_lat=points["A"][0]):
    # Calcul de la distance à partir du centre (ex: point A)
    return np.sqrt((lons - center_lon) ** 2 + (lats - center_lat) ** 2)

# Calcul des valeurs pour chaque point de la grille
values = example_function(lon_grid, lat_grid)

# Créer une carte avec une projection Plate Carrée
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Étendre les limites géographiques pour voir toute la zone autour des points A, B, C, D, STRA et STRE
ax.set_extent([lon_min - 0.01, lon_max + 0.01, lat_min - 0.01, lat_max + 0.01], crs=ccrs.PlateCarree())  # Ajuster l'étendue pour mieux voir la région

# Ajouter des caractéristiques géographiques de base
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')

# Tracer les lignes entre les points A, B, C, D
lons, lats = zip(*[points["A"], points["C"], points["D"], points["B"], points["A"]])  # Ajouter A à la fin pour fermer le polygone
ax.plot(lons, lats, marker='o', color='blue', markersize=8, label="Sciara del Fuoco", transform=ccrs.PlateCarree(), linewidth=2)

# Ajouter les points de façon annotée
for point, (lat, lon) in points.items():
    ax.text(lon, lat, f"{point}", transform=ccrs.PlateCarree(), fontsize=12, color='red', weight='bold', ha='center')

# Tracer les points de la grille
ax.scatter(lon_grid, lat_grid, color='green', s=1, label="Points de la grille", transform=ccrs.PlateCarree())

# Tracer les contours de la grille de valeurs
contour = ax.contour(lon_grid, lat_grid, values, 10, transform=ccrs.PlateCarree(), cmap='coolwarm')

# Ajouter un titre
plt.title("Carte de la Sciara del Fuoco avec Meshgrid Espacée de 10 mètres", fontsize=16)

# Afficher la légende pour les contours
plt.colorbar(contour, ax=ax, orientation="vertical", label="Valeurs calculées")

# Afficher la carte avec la légende
plt.legend(loc='lower right')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Coordonnées des points A, B, C, D, STRA et STRE
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),  # Vers la mer
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),  # Vers la mer
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),  # Vers le sommet
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),  # Vers le sommet
    "STRA": (38 + 47/60 + 42/3600, 15 + 13/60 + 1/3600),  # Point STRA
    "STRE": (38 + 48/60 + 8/3600, 15 + 12/60 + 54/3600),  # Point STRE
}

# Extraire les coordonnées minimales et maximales pour la grille
lons = [lon for _, lon in points.values()]
lats = [lat for lat, _ in points.values()]

lon_min, lon_max = min(lons), max(lons)
lat_min, lat_max = min(lats), max(lats)

# Calculer les espacements en degrés pour 10 mètres
lat_spacing = 10 / 111000  # Espacement en degrés pour la latitude (10 mètres)
avg_lat = np.mean([lat_min, lat_max])  # Latitude moyenne
lon_spacing = 10 / (111000 * np.cos(np.radians(avg_lat)))  # Espacement en degrés pour la longitude (10 mètres)

# Créer une grille de points entre les limites avec un espacement de 10m
lon_grid, lat_grid = np.meshgrid(np.arange(lon_min, lon_max, lon_spacing),
                                 np.arange(lat_min, lat_max, lat_spacing))

# Fonction pour calculer la distance à une station
def calculate_distance(lons, lats, lon_station, lat_station):
    # Calcul de la distance euclidienne
    return np.sqrt((lons - lon_station)**2 + (lats - lat_station)**2)

# Calcul des distances à STRA et STRE pour chaque point de la grille
r_stra = calculate_distance(lon_grid, lat_grid, points["STRA"][1], points["STRA"][0])
r_stre = calculate_distance(lon_grid, lat_grid, points["STRE"][1], points["STRE"][0])

# Calcul de la valeur pour chaque point de la grille
value_grid = np.sqrt(r_stra / r_stre)

# Créer une carte avec une projection Plate Carrée
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Étendre les limites géographiques pour voir toute la zone autour des points A, B, C, D, STRA et STRE
ax.set_extent([lon_min - 0.01, lon_max + 0.01, lat_min - 0.01, lat_max + 0.01], crs=ccrs.PlateCarree())  # Ajuster l'étendue pour mieux voir la région

# Ajouter des caractéristiques géographiques de base
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')

# Tracer les lignes entre les points A, B, C, D
lons, lats = zip(*[points["A"], points["C"], points["D"], points["B"], points["A"]])  # Ajouter A à la fin pour fermer le polygone
ax.plot(lons, lats, marker='o', color='blue', markersize=8, label="Sciara del Fuoco", transform=ccrs.PlateCarree(), linewidth=2)

# Ajouter les points de façon annotée
for point, (lat, lon) in points.items():
    ax.text(lon, lat, f"{point}", transform=ccrs.PlateCarree(), fontsize=12, color='red', weight='bold', ha='center')

# Tracer les points de la grille
ax.scatter(lon_grid, lat_grid, color='green', s=1, label="Points de la grille", transform=ccrs.PlateCarree())

# Tracer les contours des valeurs
contour = ax.contour(lon_grid, lat_grid, value_grid, 10, transform=ccrs.PlateCarree(), cmap='coolwarm')

# Ajouter un titre
plt.title("Carte de la Sciara del Fuoco avec Valeurs (rSTRA / rSTRE)", fontsize=16)

# Afficher la légende pour les contours
plt.colorbar(contour, ax=ax, orientation="vertical", label="Valeur (rSTRA / rSTRE)")

# Afficher la carte avec la légende
plt.legend(loc='lower right')
plt.show()

