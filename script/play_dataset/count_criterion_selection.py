import pandas as pd

# Fonction pour compter le nombre de landslides avec un ratio <= 6.5 et RRSAM_G > 875
def count_landslides(file_path):
    # Charger le fichier CSV dans un DataFrame
    df = pd.read_csv(file_path)
    
    # Appliquer les deux filtres :
    # 1. Ratio <= 6.5
    # 2. RRSAM_G > 875
    filtered_df = df[(df['Ratio'] <= 6.5) & (df['RSAM_G'] > 875)]
    
    # Compter le nombre de lignes dans le DataFrame filtré (chaque ligne est un landslide)
    number_of_landslides = len(filtered_df)
    
    return number_of_landslides

# Chemin du fichier CSV
file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra_0.5/strg_stra_all_peaks_data.csv'

# Appeler la fonction pour compter les landslides
landsides_count = count_landslides(file_path)

# Afficher le résultat
print(f"Le nombre de landslides (avec ratio <= 6.5 et RSAM_G > 875) est : {landsides_count}")
