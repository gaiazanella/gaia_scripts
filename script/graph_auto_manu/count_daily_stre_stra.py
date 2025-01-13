import csv
import numpy as np

# Nom du fichier à ouvrir
file_name = "2020_auto_stre_stra_1sec_filtered.csv"

# Initialiser une liste pour stocker les valeurs de la colonne 'frane'
frane_values = []

# Ouvrir le fichier en mode lecture
with open(file_name, mode='r') as file:
    # Créer un lecteur CSV
    reader = csv.DictReader(file)  # Utilisation de DictReader pour accéder aux colonnes par nom
    
    # Parcourir chaque ligne du fichier et ajouter les valeurs de la colonne 'frane' à la liste
    for row in reader:
        frane_values.append(float(row['frane']))

# Vérifier que la liste n'est pas vide avant de calculer
if frane_values:
    # Calcul de la moyenne
    mean_frane = np.mean(frane_values)
    
    # Calcul des quartiles
    Q1 = np.percentile(frane_values, 25)  # Premier quartile (25%)
    Q3 = np.percentile(frane_values, 75)  # Troisième quartile (75%)
    
    # Calcul de l'écart-type
    std_dev = np.std(frane_values)

    # Calcul des valeurs minimales et maximales
    min_frane = np.min(frane_values)
    max_frane = np.max(frane_values)

    # Afficher les résultats
    print(f"La moyenne des glissements de terrain est : {mean_frane}")
    print(f"Le premier quartile (Q1) des glissements de terrain est : {Q1}")
    print(f"Le troisième quartile (Q3) des glissements de terrain est : {Q3}")
    print(f"L'écart-type des glissements de terrain est : {std_dev}")
    print(f"La valeur minimale des glissements de terrain est : {min_frane}")
    print(f"La valeur maximale des glissements de terrain est : {max_frane}")
else:
    print("Le fichier ne contient aucune donnée.")
