import numpy as np
import matplotlib.pyplot as plt
import pyproj

# Définir la projection WGS84 et UTM (par exemple zone 33N, mais adapte selon ta région)
wgs84 = pyproj.Proj(proj="latlong", datum="WGS84")
utm = pyproj.Proj(proj="utm", zone=33, datum="WGS84")  # Change la zone UTM si nécessaire

# Points (en latitude, longitude)
points = {
    "A": (38 + 48/60 + 25/3600, 15 + 12/60 + 36/3600),
    "B": (38 + 47/60 + 47/3600, 15 + 12/60 + 55/3600),
    "C": (38 + 47/60 + 50/3600, 15 + 11/60 + 52/3600),
    "D": (38 + 47/60 + 30/3600, 15 + 12/60 + 30/3600),
}

# Convertir les points (lat, lon) en UTM (mètres)
utm_points = {}
for point, (lat, lon) in points.items():
    x, y = pyproj.transform(wgs84, utm, lon, lat)
    utm_points[point] = (x, y)

# Extraire les coordonnées UTM (en mètres)
A_m = utm_points["A"]
B_m = utm_points["B"]
C_m = utm_points["C"]
D_m = utm_points["D"]

# Plage en mètres
range_lat_m = max(A_m[1], B_m[1], C_m[1], D_m[1]) - min(A_m[1], B_m[1], C_m[1], D_m[1])
range_lon_m = max(A_m[0], B_m[0], C_m[0], D_m[0]) - min(A_m[0], B_m[0], C_m[0], D_m[0])

# Espacement souhaité en mètres
spacing = 10  # Espacement entre les points en mètres

# Calcul du nombre de points pour la grille
n_lat = int(range_lat_m / spacing) + 1
n_lon = int(range_lon_m / spacing) + 1

# Création de la grille en mètres
lat_grid_m = np.linspace(min(A_m[1], B_m[1], C_m[1], D_m[1]), max(A_m[1], B_m[1], C_m[1], D_m[1]), n_lat)
lon_grid_m = np.linspace(min(A_m[0], B_m[0], C_m[0], D_m[0]), max(A_m[0], B_m[0], C_m[0], D_m[0]), n_lon)
LAT_m, LON_m = np.meshgrid(lat_grid_m, lon_grid_m)

# Surface plate
Z = np.zeros_like(LON_m)  # Créer une surface plate à altitude zéro

# Visualisation
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Tracer la surface plate
ax.plot_surface(LON_m, LAT_m, Z, cmap='terrain')

# Ajouter les points A, B, C, D sur la grille
ax.scatter(B_m[0], B_m[1], 0, color='red', s=100, label='B')  # Point B
ax.scatter(A_m[0], A_m[1], 0, color='blue', s=100, label='A')  # Point A
ax.scatter(C_m[0], C_m[1], 0, color='green', s=100, label='C')  # Point C
ax.scatter(D_m[0], D_m[1], 0, color='purple', s=100, label='D')  # Point D

# Labels et titres
ax.set_xlabel("Distance East-West (m)")
ax.set_ylabel("Distance North-South (m)")
ax.set_zlabel("Elevation (m)")
ax.set_title(f"Flat Meshgrid (Spacing: {spacing} m)")

# Légende
ax.legend()

plt.show()
