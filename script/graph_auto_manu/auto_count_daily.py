import pandas as pd

# Charger le fichier CSV
file_path = '/home/gaia/Documents/processing_1_sec/2020/double_durations_speed_strg_stre/strg_stre_all_peaks_data.csv'
data = pd.read_csv(file_path)

# Extraire la date sans l'heure de la colonne 'Peak _Time_UTC'
data['Date'] = pd.to_datetime(data['Peak_Time_UTC']).dt.date

# Compter les occurrences par jour
daily_counts = data['Date'].value_counts().sort_index()

# Créer un nouveau DataFrame avec les résultats
result = pd.DataFrame({
    'Date': daily_counts.index,
    'frane': daily_counts.values
})

# Sauvegarder le DataFrame dans un nouveau fichier CSV
output_file = '/home/gaia/Documents/processing_10_sec/2020/double_durations_speed_strg_stre/strg_stre_2020_auto.csv'
result.to_csv(output_file, index=False)

print(f"Le fichier {output_file} a été créé avec succès.")
