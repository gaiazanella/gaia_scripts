### PACKAGES
from scipy.signal import find_peaks
import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

## Paramètres de base
start_date = datetime(2020, 1, 1)  # Date de début
end_date = datetime(2021, 1, 1)   # Date de fin
#output_dir = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra_test' 
#output_dir = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra_test_0.1'  # Répertoire de sortie
#output_dir = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra_test_0.15'
output_dir = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_strg_stra_test_0.2'
# Paramètres pour la détection des pics
distance_min = 1  # Ajuster cette valeur si nécessaire
#prominence = 0.5
#prominence = 0.1
#prominence= 0.15
prominence = 0.2

# Fonction pour trouver le début et la fin d'un pic
def find_peak_edges(df_ratio, peak, threshold=0.001):
    start_index = peak
    end_index = peak
    
    # Trouver le début du pic
    while start_index > 0 and (df_ratio['ratio_8_15Hz'].iloc[start_index] >= df_ratio['ratio_8_15Hz'].iloc[start_index - 1] or
                               df_ratio['ratio_8_15Hz'].iloc[peak] - df_ratio['ratio_8_15Hz'].iloc[start_index] <= threshold):
        start_index -= 1
        
    # Trouver la fin du pic
    while end_index < len(df_ratio['ratio_8_15Hz']) - 1 and (df_ratio['ratio_8_15Hz'].iloc[end_index] >= df_ratio['ratio_8_15Hz'].iloc[end_index + 1] or
                               df_ratio['ratio_8_15Hz'].iloc[peak] - df_ratio['ratio_8_15Hz'].iloc[end_index] <= threshold):
        end_index += 1
        
    return start_index, end_index

def process_data(file_A, file_G, output_file):
    # Chargement des fichiers
    df_A = pd.read_csv(file_A)
    df_G = pd.read_csv(file_G)

    # Assurez-vous que le format de la colonne 'time_UTC' est le même
    df_A['time_UTC'] = pd.to_datetime(df_A['time_UTC'])
    df_G['time_UTC'] = pd.to_datetime(df_G['time_UTC'])

    # Calculer le ratio
    df_ratio = pd.DataFrame()
    df_ratio['time_UTC'] = df_A['time_UTC']
    df_ratio['ratio_8_15Hz'] = df_G['RSAM_env_smooth_8-15Hz'] / df_A['RSAM_env_smooth_8-15Hz']

    # Détection des pics avec les nouveaux paramètres sur le ratio brut
    peaks_8_15Hz, properties_8_15Hz = find_peaks(df_ratio['ratio_8_15Hz'], prominence=prominence, distance=distance_min)
    ratio = df_ratio['ratio_8_15Hz'].iloc[peaks_8_15Hz].values

    # Créer des listes pour stocker les temps de début, de fin et les durées des pics
    initial_peak_times = []
    final_peak_times = []
    durations = []

    # Boucle pour chaque pic détecté
    for peak in peaks_8_15Hz:
        # Utiliser la fonction find_peak_edges pour trouver les indices de début et de fin
        start_index, end_index = find_peak_edges(df_ratio, peak)

        # Calculer les temps de début et de fin en UTC
        initial_peak_time = df_ratio['time_UTC'].iloc[start_index]
        final_peak_time = df_ratio['time_UTC'].iloc[end_index]

        # Calculer la durée du pic en secondes
        duration = (final_peak_time - initial_peak_time).total_seconds()

        # Ajouter les temps de début, de fin et la durée aux listes
        initial_peak_times.append(initial_peak_time)
        final_peak_times.append(final_peak_time)
        durations.append(duration)

    # Créer des listes pour stocker les temps de début, de fin et les durées des pics pour duration_w
    initial_peak_times_w = []
    final_peak_times_w = []
    durations_w = []

    # Boucle pour chaque pic détecté
    for i_w, peak_w in enumerate(peaks_8_15Hz):
        # Utiliser l'indice i pour accéder à peak_amplitudes
        threshold_w = 0.5 * ratio[i_w] ## on calcule un seuil relatif à la moitié de l'amplitude du pic.
        ## Ce seuil est utilisé pour définir juusqu'où le pic se prolonge en amplitude. 

        # Trouver le début du pic
        start_index_w = peak_w
        while start_index_w > 0 and df_ratio['ratio_8_15Hz'].iloc[start_index_w] >= threshold_w:
            start_index_w -= 1

        # Assurer que start_index ne sort pas des limites
        if start_index_w < 0:
            start_index_w = 0

        # Trouver la fin du pic
        end_index_w = peak_w
        while end_index_w < len(df_ratio['ratio_8_15Hz']) - 1 and df_ratio['ratio_8_15Hz'].iloc[end_index_w] >= threshold_w:
            end_index_w += 1

        # Assurer que end_index ne sort pas des limites
        if end_index_w >= len(df_ratio['ratio_8_15Hz']):
            end_index_w = len(df_ratio['ratio_8_15Hz']) - 1

        # Calculer les temps de début et de fin en UTC
        initial_peak_time_w = df_ratio['time_UTC'].iloc[start_index_w + 1] if start_index_w + 1 < len(df_ratio) else df_ratio['time_UTC'].iloc[start_index_w]
        final_peak_time_w = df_ratio['time_UTC'].iloc[end_index_w - 1] if end_index_w - 1 >= 0 else df_ratio['time_UTC'].iloc[end_index_w]

        # Calculer la durée du pic en secondes
        duration_w = (final_peak_time_w - initial_peak_time_w).total_seconds()

        # Ajouter les temps de début, de fin et la durée aux listes
        initial_peak_times_w.append(initial_peak_time_w)
        final_peak_times_w.append(final_peak_time_w)
        durations_w.append(duration_w)

    # Créer un DataFrame pour les pics avec les nouvelles colonnes
    peaks_df = pd.DataFrame({
        'Peak_Time_UTC': df_ratio['time_UTC'].iloc[peaks_8_15Hz],
        'Ratio': ratio,
        'RSAM_A': df_A['RSAM_env_smooth_8-15Hz'].iloc[peaks_8_15Hz].values,
        'RSAM_G': df_G['RSAM_env_smooth_8-15Hz'].iloc[peaks_8_15Hz].values,
        'Duration': durations,
        'Initial_Peak_Time': initial_peak_times,
        'Final_Peak_Time': final_peak_times,
        'Duration_w': durations_w,
        'Initial_Peak_Time_w': initial_peak_times_w,
        'Final_Peak_Time_w': final_peak_times_w
    })

    # Assurez-vous que les colonnes de temps sont au format datetime
    peaks_df['Peak_Time_UTC'] = pd.to_datetime(peaks_df['Peak_Time_UTC'])
    peaks_df['Initial_Peak_Time'] = pd.to_datetime(peaks_df['Initial_Peak_Time'])
    peaks_df['Initial_Peak_Time_w'] = pd.to_datetime(peaks_df['Initial_Peak_Time_w'])

    # Calculer la durée en secondes pour chaque ensemble de pics
    peaks_df['sp_duration_seconds'] = (peaks_df['Peak_Time_UTC'] - peaks_df['Initial_Peak_Time']).dt.total_seconds()

    # Calculer la vitesse pour Initial_Peak_Time
    peaks_df['speed_m/s'] = 808 / peaks_df['sp_duration_seconds']

    # Calculer la durée en secondes pour Initial_Peak_Time_w
    peaks_df['sp_duration_seconds_w'] = (peaks_df['Peak_Time_UTC'] - peaks_df['Initial_Peak_Time_w']).dt.total_seconds()

    # Calculer la vitesse pour Initial_Peak_Time_w
    peaks_df['speed_m/s_w'] = 808 / peaks_df['sp_duration_seconds_w']

    # Enregistrer le DataFrame final filtré dans un fichier CSV
    peaks_df.to_csv(output_file, index=False)

# Boucle pour chaque jour entre start_date et end_date
for single_date in pd.date_range(start_date, end_date):
    date_str = single_date.strftime('%Y%m%d')  # Format YYYYMMDD

    # Chemins vers les fichiers pour la date actuelle
    chemin_vers_les_fichiers_A = f'/home/gaia/Documents/processing_10_sec/2020/rsam_test/rsam_STRA_{date_str}*.csv'
    chemin_vers_les_fichiers_G = f'/home/gaia/Documents/processing_10_sec/2020/rsam_test/rsam_STRG_{date_str}*.csv'

    # Récupérer tous les fichiers correspondants
    fichiers_A = glob.glob(chemin_vers_les_fichiers_A)
    fichiers_G = glob.glob(chemin_vers_les_fichiers_G)

    # Assurez-vous qu'il y a un fichier pour chaque station
    if fichiers_A and fichiers_G:
        output_file = os.path.join(output_dir, f'strg_stra_peaks_data_{date_str}.csv')
        process_data(fichiers_A[0], fichiers_G[0], output_file)

# Combiner tous les fichiers CSV résultants en un seul fichier
all_files = glob.glob(os.path.join(output_dir, "strg_stra_peaks_data_*.csv"))

# Créer une liste pour stocker les DataFrames non vides
dataframes = []

# Lire chaque fichier et ajouter uniquement les DataFrames non vides
for f in all_files:
    df = pd.read_csv(f)
    if not df.empty and not df.isnull().all(axis=None):  # Vérifier que le DataFrame n'est pas vide et ne contient pas que des NA
        dataframes.append(df)

# Concaténer les DataFrames valides
if dataframes:  # Vérifiez si la liste n'est pas vide
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Convertir la colonne Peak_Time_UTC en datetime pour le tri
    combined_df['Peak_Time_UTC'] = pd.to_datetime(combined_df['Peak_Time_UTC'])
    
    # Trier le DataFrame par Peak_Time_UTC
    combined_df.sort_values(by='Peak_Time_UTC', inplace=True)

    # Réinitialiser l'index après le tri
    combined_df.reset_index(drop=True, inplace=True)
    
    # Enregistrer le fichier combiné trié
    combined_output_file = os.path.join(output_dir, 'strg_stra_all_peaks_data.csv')
    combined_df.to_csv(combined_output_file, index=False)
else:
    print("Aucun fichier valide à combiner.")
