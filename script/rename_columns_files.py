import pandas as pd
import glob

# Chemin du dossier contenant les fichiers CSV
chemin_dossier = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed'

# Obtenir la liste de tous les fichiers CSV correspondant au motif
fichiers_csv = glob.glob(chemin_dossier + "peaks_data_*.csv")

# Boucle pour traiter chaque fichier
for fichier in fichiers_csv:
    # Lire le fichier CSV
    df = pd.read_csv(fichier)
    
    # Renommer les colonnes souhaitées
    df.rename(columns={'duration_seconds': 'sp_duration_seconds', 'duration_seconds_w': 'sp_duration_seconds_w'}, inplace=True)
    
    # Sauvegarder les changements en écrasant le fichier original, ou sauvegarder dans un nouveau fichier
    df.to_csv(fichier, index=False)
    print(f"Colonnes renommées pour le fichier : {fichier}")

