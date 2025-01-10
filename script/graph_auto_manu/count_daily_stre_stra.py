import csv

# Nom du fichier à ouvrir
file_name = "2020_auto_stre_stra_1sec_filtered.csv"

# Initialiser des variables pour la somme et le comptage des valeurs
total_glissements = 0
nombre_de_lignes = 0

# Ouvrir le fichier en mode lecture
with open(file_name, mode='r') as file:
    # Créer un lecteur CSV
    reader = csv.DictReader(file)  # Utilisation de DictReader pour accéder aux colonnes par nom
    
    # Parcourir chaque ligne du fichier
    for row in reader:
        # Ajouter la valeur de la colonne 'frane' à la somme (en supposant que les valeurs sont numériques)
        total_glissements += float(row['frane'])
        # Incrémenter le compteur de lignes
        nombre_de_lignes += 1

# Calculer la moyenne, si le nombre de lignes est supérieur à 0
if nombre_de_lignes > 0:
    moyenne_glissements = total_glissements / nombre_de_lignes
    print(f"La valeur moyenne des glissements de terrain est : {moyenne_glissements}")
else:
    print("Le fichier ne contient aucune donnée.")
