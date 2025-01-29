import pandas as pd

# Chemin du fichier CSV original
file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/all_peaks_copy.csv'

# Charger le fichier CSV dans un DataFrame
data = pd.read_csv(file_path)

# Liste des colonnes à supprimer
columns_to_remove = ['Duration_w', 'Initial_Peak_Time_w', 'Final_Peak_Time_w', 
                     'speed_m/s', 'speed_m/s_w', 'duration_seconds_w']

# Supprimer les colonnes spécifiées
data = data.drop(columns=columns_to_remove, errors='ignore')

# Dictionnaire de renommage des colonnes
columns_rename = {
    'RSAM_A': 'RSAM_STRA',
    'RSAM_E': 'RSAM_STRE',
    'duration_seconds': 'duration_initial_maxpeak'
}

# Renommer les colonnes spécifiées
data = data.rename(columns=columns_rename)

# Enregistrer le DataFrame modifié dans un nouveau fichier CSV
output_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/all_peaks_copy_modif.csv'
data.to_csv(output_file_path, index=False)

print(f"Les colonnes ont été supprimées et renommées, et le fichier a été enregistré sous {output_file_path}")
