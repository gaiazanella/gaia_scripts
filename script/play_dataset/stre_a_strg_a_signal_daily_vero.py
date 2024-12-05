import pandas as pd
import os

# Définir le chemin du dossier contenant les fichiers
input_dir = '/home/gaia/Documents/processing_1_sec/2020/rsam/'
output_dir = '/home/gaia/Documents/processing_1_sec/2020/rsam_ratio/'

# Créer une liste de tous les jours de 2020 en utilisant pd.date_range pour obtenir des dates valides
days_2020 = pd.date_range('2020-01-01', '2020-12-31', freq='D').strftime('%Y%m%d').tolist()

# Fonction pour traiter un fichier pour chaque jour
def process_day(day):
    try:
        # Charger les fichiers CSV pour la journée
        file_path_stra = os.path.join(input_dir, f'rsam_STRA_{day}.csv')
        file_path_stre = os.path.join(input_dir, f'rsam_STRE_{day}.csv')
        file_path_strg = os.path.join(input_dir, f'rsam_STRG_{day}.csv')

        data_stra = pd.read_csv(file_path_stra)
        data_stre = pd.read_csv(file_path_stre)
        data_strg = pd.read_csv(file_path_strg)

        # Vérification que les colonnes nécessaires existent dans les fichiers
        if 'time_UTC' not in data_stra.columns or 'RSAM_env_smooth_8-15Hz' not in data_stra.columns:
            raise ValueError(f"Les colonnes 'time_UTC' ou 'RSAM_env_smooth_8-15Hz' sont manquantes dans le fichier {file_path_stra}.")
        if 'RSAM_env_smooth_8-15Hz' not in data_stre.columns:
            raise ValueError(f"La colonne 'RSAM_env_smooth_8-15Hz' est manquante dans le fichier {file_path_stre}.")
        if 'RSAM_env_smooth_8-15Hz' not in data_strg.columns:
            raise ValueError(f"La colonne 'RSAM_env_smooth_8-15Hz' est manquante dans le fichier {file_path_strg}.")

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

        # Enregistrer dans un nouveau fichier CSV pour le jour
        output_file_path = os.path.join(output_dir, f'rsam_ratio_stre_strg_{day}.csv')
        final_data.to_csv(output_file_path, index=False)

        # Afficher un message de confirmation
        print(f"Le fichier CSV pour le {day} a été créé avec succès et sauvegardé à {output_file_path}.")

        return final_data  # Retourner les données du jour pour combiner plus tard

    except Exception as e:
        print(f"Erreur pour le fichier {day}: {e}")
        return None

# Fonction pour regrouper tous les fichiers créés dans un fichier global pour l'année
def combine_all_days():
    all_data = []
    
    # Traiter chaque jour de 2020
    for day in days_2020:
        daily_data = process_day(day)
        if daily_data is not None:
            all_data.append(daily_data)
    
    # Combiner toutes les données dans un seul DataFrame
    if all_data:
        yearly_data = pd.concat(all_data, ignore_index=True)
        yearly_output_path = os.path.join(output_dir, 'rsam_ratio_all_2020.csv')
        
        # Enregistrer le DataFrame combiné dans un fichier CSV
        yearly_data.to_csv(yearly_output_path, index=False)
        
        print(f"Le fichier global pour l'année 2020 a été créé avec succès et sauvegardé à {yearly_output_path}.")
    else:
        print("Aucune donnée n'a été traitée pour l'année 2020.")

# Lancer le traitement pour tous les jours et créer le fichier global
combine_all_days()
