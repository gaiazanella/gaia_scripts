import pandas as pd
import matplotlib.pyplot as plt
import os

# Charger le fichier 'all_peaks.csv'
file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/all_peaks.csv'
data = pd.read_csv(file_path)

# Filtrer les données en fonction des critères 'RSAM_E > 875' et 'Ratio < 6.5'
filtered_data = data[(data['RSAM_E'] > 875) & (data['Ratio'] < 6.5)]

# Vérifiez que la colonne Peak_Time_UTC existe et est correcte
if 'Peak_Time_UTC' not in data.columns:
    raise ValueError("The column 'Peak_Time_UTC' is missing in the loaded file.")

# Extraire la date sans l'heure de la colonne 'Peak_Time_UTC'
filtered_data['Date'] = pd.to_datetime(filtered_data['Peak_Time_UTC']).dt.date

# Compter les occurrences par jour
daily_counts = filtered_data['Date'].value_counts().sort_index()

# Créer un DataFrame avec les résultats et sauvegarder dans '2020_auto.csv'
result_auto = pd.DataFrame({
    'Date': pd.to_datetime(daily_counts.index),
    'frane': daily_counts.values
}).sort_values('Date')
auto_output_path = '/home/gaia/Documents/2020_auto.csv'
result_auto.to_csv(auto_output_path, index=False)

# Charger le fichier '2020_manual.csv'
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Vérifiez que les colonnes nécessaires existent dans les fichiers
if 'Date' not in manual_data.columns or 'frane' not in manual_data.columns:
    raise ValueError("The columns 'Date' and/or 'frane' are missing in the file '2020_manual.csv'.")

if 'Date' not in result_auto.columns or 'frane' not in result_auto.columns:
    raise ValueError("The columns 'Date' and/or 'frane' are missing in the file '2020_auto.csv'.")

# Convertir les colonnes 'Date' en datetime pour s'assurer de la cohérence
result_auto['Date'] = pd.to_datetime(result_auto['Date'])
manual_data['Date'] = pd.to_datetime(manual_data['Date'])

# Calculer la moyenne mobile hebdomadaire pour le graphique uniquement
manual_data.set_index('Date', inplace=True)
manual_data['frane_rolling'] = manual_data['frane'].rolling(window=7).mean()

result_auto.set_index('Date', inplace=True)
auto_rolling = result_auto['frane'].rolling(window=7).mean()  # Moyenne glissante pour le graphique seulement

# Calculer le nombre total de 'frane' pour l'année
total_manual_frane = manual_data['frane'].sum()
total_auto_frane = result_auto['frane'].sum()

# Tracer le graphique
plt.figure(figsize=(12, 8))

# Tracer uniquement les moyennes hebdomadaires
plt.plot(result_auto.index, auto_rolling, label='2020 Auto - Weekly Average', color='cyan', linewidth=2)
plt.plot(manual_data.index, manual_data['frane_rolling'], label='2020 Manual - Weekly Average', color='grey', linewidth=2)

# Ajouter les contraintes dans le titre
title = 'Comparison of Landslide Detections (Weekly Average)\nRSAM_E > 875, Ratio (E/A) < 6.5'

# Configurer le graphique
plt.title(title)
plt.xlabel('Date')
plt.ylabel('Number of Landslides (Frane)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotate dates for better readability
plt.tight_layout()

# Définir le chemin d'enregistrement de l'image
save_path = '/home/gaia/Documents/processing_1_sec/2020/landslide_comparison.jpg'

# Vérifier si le répertoire existe, sinon le créer
save_dir = os.path.dirname(save_path)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Enregistrer la figure en format JPEG
plt.savefig(save_path, format='jpeg')

# Afficher le graphique
plt.show()

# Afficher le nombre total de 'frane' pour l'année
print(f"Total number of 'frane' for 2020 (Manual): {total_manual_frane}")
print(f"Total number of 'frane' for 2020 (Auto): {total_auto_frane}")
