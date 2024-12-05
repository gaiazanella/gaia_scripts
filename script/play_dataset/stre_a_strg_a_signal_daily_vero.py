import pandas as pd

# Charger les fichiers CSV
file_path_stra = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRA_20200101.csv'
file_path_stre = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRE_20200101.csv'
file_path_strg = '/home/gaia/Documents/processing_1_sec/2020/rsam/rsam_STRG_20200101.csv'  # Nouveau fichier pour STRG

data_stra = pd.read_csv(file_path_stra)
data_stre = pd.read_csv(file_path_stre)
data_strg = pd.read_csv(file_path_strg)  # Charger le fichier STRG

# Vérification que les colonnes nécessaires existent dans les fichiers
if 'time_UTC' not in data_stra.columns or 'RSAM_env_smooth_8-15Hz' not in data_stra.columns:
    raise ValueError("Les colonnes 'time_UTC' ou 'RSAM_env_smooth_8-15Hz' sont manquantes dans le fichier rsam_STRA_20200101.csv.")
if 'RSAM_env_smooth_8-15Hz' not in data_stre.columns:
    raise ValueError("La colonne 'RSAM_env_smooth_8-15Hz' est manquante dans le fichier rsam_STRE_20200101.csv.")
if 'RSAM_env_smooth_8-15Hz' not in data_strg.columns:
    raise ValueError("La colonne 'RSAM_env_smooth_8-15Hz' est manquante dans le fichier rsam_STRG_20200101.csv.")

# Fusionner les trois DataFrames sur la colonne 'time_UTC'
merged_data = pd.merge(data_stra[['time_UTC', 'RSAM_env_smooth_8-15Hz']], 
                       data_stre[['time_UTC', 'RSAM_env_smooth_8-15Hz']], 
                       on='time_UTC', 
                       suffixes=('_STRA', '_STRE'))

# Fusionner avec STRG et renommer la colonne pour correspondre au format attendu
merged_data = pd.merge(merged_data, 
                       data_strg[['time_UTC', 'RSAM_env_smooth_8-15Hz']], 
                       on='time_UTC')

# Renommer la colonne de STRG pour qu'elle soit cohérente avec les autres colonnes
merged_data.rename(columns={'RSAM_env_smooth_8-15Hz': 'RSAM_env_smooth_8-15Hz_STRG'}, inplace=True)

# Calculer les ratios entre les colonnes RSAM
merged_data['Ratio_STRE_STRA'] = merged_data['RSAM_env_smooth_8-15Hz_STRE'] / merged_data['RSAM_env_smooth_8-15Hz_STRA']
merged_data['Ratio_STRG_STRA'] = merged_data['RSAM_env_smooth_8-15Hz_STRG'] / merged_data['RSAM_env_smooth_8-15Hz_STRA']

# Créer un nouveau DataFrame avec les colonnes souhaitées dans le bon ordre
final_data = merged_data[['time_UTC', 
                          'RSAM_env_smooth_8-15Hz_STRA', 
                          'RSAM_env_smooth_8-15Hz_STRE', 
                          'RSAM_env_smooth_8-15Hz_STRG', 
                          'Ratio_STRE_STRA', 
                          'Ratio_STRG_STRA']]

# Enregistrer dans un nouveau fichier CSV
output_file_path = '/home/gaia/Documents/processing_1_sec/2020/rsam_ratio/rsam_ratio_stre_strg_20200101.csv'
final_data.to_csv(output_file_path, index=False)

# Afficher un message de confirmation
print(f"Le fichier CSV a été créé avec succès et sauvegardé à {output_file_path}.")
