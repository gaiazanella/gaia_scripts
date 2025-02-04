import pandas as pd
import os
import numpy as np

# Définir le chemin du dossier contenant les fichiers
input_dir = '/home/gaia/Documents/processing_10_sec/2020/rsam_test/'
output_dir = '/home/gaia/Documents/processing_10_sec/2020/rsam_ratio_test'

# Créer une liste de tous les jours de 2020
days_2020 = pd.date_range('2020-01-01', '2020-12-31', freq='D').strftime('%Y%m%d').tolist()

def process_day(day):
    try:
        # Initialisation des DataFrames avec des NaN par défaut
        data_stra = data_stre = data_strg = data_strc = pd.DataFrame(columns=['time_UTC', 'RSAM_env_smooth_8-15Hz'])
        
        # Vérification de l'existence des fichiers et chargement des données
        file_path_stra = os.path.join(input_dir, f'rsam_STRA_{day}.csv')
        file_path_stre = os.path.join(input_dir, f'rsam_STRE_{day}.csv')
        file_path_strg = os.path.join(input_dir, f'rsam_STRG_{day}.csv')
        file_path_strc = os.path.join(input_dir, f'rsam_STRC_{day}.csv')

        if os.path.exists(file_path_stra):
            data_stra = pd.read_csv(file_path_stra)
        if os.path.exists(file_path_stre):
            data_stre = pd.read_csv(file_path_stre)
        if os.path.exists(file_path_strg):
            data_strg = pd.read_csv(file_path_strg)
        if os.path.exists(file_path_strc):
            data_strc = pd.read_csv(file_path_strc)

        # Vérification des colonnes nécessaires
        if 'time_UTC' not in data_stra.columns or 'RSAM_env_smooth_8-15Hz' not in data_stra.columns:
            raise ValueError(f"Les colonnes nécessaires sont manquantes dans le fichier {file_path_stra}.")
        if 'RSAM_env_smooth_8-15Hz' not in data_stre.columns:
            raise ValueError(f"La colonne nécessaire est manquante dans le fichier {file_path_stre}.")
        if 'RSAM_env_smooth_8-15Hz' not in data_strg.columns:
            raise ValueError(f"La colonne nécessaire est manquante dans le fichier {file_path_strg}.")
        if 'RSAM_env_smooth_8-15Hz' not in data_strc.columns:
            raise ValueError(f"La colonne nécessaire est manquante dans le fichier {file_path_strc}.")

        # Renommer les colonnes pour chaque station afin de les identifier
        data_stra.rename(columns={'RSAM_env_smooth_8-15Hz': 'RSAM_env_smooth_8-15Hz_STRA'}, inplace=True)
        data_stre.rename(columns={'RSAM_env_smooth_8-15Hz': 'RSAM_env_smooth_8-15Hz_STRE'}, inplace=True)
        data_strg.rename(columns={'RSAM_env_smooth_8-15Hz': 'RSAM_env_smooth_8-15Hz_STRG'}, inplace=True)
        data_strc.rename(columns={'RSAM_env_smooth_8-15Hz': 'RSAM_env_smooth_8-15Hz_STRC'}, inplace=True)

        # Fusionner les DataFrames
        merged_data = pd.merge(data_stra[['time_UTC', 'RSAM_env_smooth_8-15Hz_STRA']], 
                               data_stre[['time_UTC', 'RSAM_env_smooth_8-15Hz_STRE']], 
                               on='time_UTC', 
                               how='outer')
        merged_data = pd.merge(merged_data, 
                               data_strg[['time_UTC', 'RSAM_env_smooth_8-15Hz_STRG']], 
                               on='time_UTC', how='outer')
        merged_data = pd.merge(merged_data, 
                               data_strc[['time_UTC', 'RSAM_env_smooth_8-15Hz_STRC']], 
                               on='time_UTC', how='outer')

        # Calculer les ratios entre les stations
        merged_data['Ratio_STRE_STRA'] = merged_data['RSAM_env_smooth_8-15Hz_STRE'] / merged_data['RSAM_env_smooth_8-15Hz_STRA']
        merged_data['Ratio_STRG_STRA'] = merged_data['RSAM_env_smooth_8-15Hz_STRG'] / merged_data['RSAM_env_smooth_8-15Hz_STRA']
        merged_data['Ratio_STRC_STRA'] = merged_data['RSAM_env_smooth_8-15Hz_STRC'] / merged_data['RSAM_env_smooth_8-15Hz_STRA']

        # Créer le DataFrame final avec les colonnes spécifiques
        final_data = merged_data[['time_UTC', 
                                  'RSAM_env_smooth_8-15Hz_STRA', 
                                  'RSAM_env_smooth_8-15Hz_STRE', 
                                  'RSAM_env_smooth_8-15Hz_STRG', 
                                  'RSAM_env_smooth_8-15Hz_STRC',  
                                  'Ratio_STRE_STRA', 
                                  'Ratio_STRG_STRA', 
                                  'Ratio_STRC_STRA']]

        # Sauvegarder les résultats dans un fichier CSV
        output_file_path = os.path.join(output_dir, f'ratio_rsam_stra_stre_strg_strc_{day}.csv')
        final_data.to_csv(output_file_path, index=False)
        print(f"Le fichier CSV pour le {day} a été créé avec succès.")
        
        return final_data

    except Exception as e:
        print(f"Erreur pour le fichier {day}: {e}")
        return None

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
        yearly_output_path = os.path.join(output_dir, 'ratio_rsam_all_2020.csv')
        yearly_data.to_csv(yearly_output_path, index=False)
        print(f"Le fichier global pour l'année 2020 a été créé avec succès.")
    else:
        print("Aucune donnée n'a été traitée pour l'année 2020.")

combine_all_days()
