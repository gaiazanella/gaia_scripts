import pandas as pd
import matplotlib.pyplot as plt
import os

# Charger le fichier 'all_peaks.csv' pour 'auto'
file_path = '/home/gaia/Documents/processing_1_sec/2021/double_duration_speed/all_peaks_data.csv'
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

# Créer un DataFrame avec les résultats 'auto' et sauvegarder dans '2020_auto.csv'
result_auto = pd.DataFrame({
    'Date': pd.to_datetime(daily_counts.index),
    'frane': daily_counts.values
}).sort_values('Date')
auto_output_path = '/home/gaia/Documents/2020_auto.csv'
result_auto.to_csv(auto_output_path, index=False)

# Convertir les colonnes 'Date' en datetime pour s'assurer de la cohérence
result_auto['Date'] = pd.to_datetime(result_auto['Date'])

# Calculer la moyenne mobile hebdomadaire pour le graphique uniquement (Auto)
result_auto.set_index('Date', inplace=True)
auto_rolling = result_auto['frane'].rolling(window=7).mean()  # Moyenne glissante pour le graphique

# Tracer le graphique pour 'auto' uniquement
plt.figure(figsize=(12, 8))

# Tracer uniquement les moyennes hebdomadaires pour 'auto'
plt.plot(result_auto.index, auto_rolling, label='2020 Auto - Weekly Average', color='orange', linewidth=2)

# Ajouter les contraintes dans le titre
title = 'Landslide Detection (Weekly Average) - Auto\nRSAM_E > 875, Ratio (E/A) < 6.5'

# Configurer le graphique
plt.title(title)
plt.xlabel('Date')
plt.ylabel('Number of Landslides (Frane)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
plt.tight_layout()

# Définir le chemin d'enregistrement de l'image
save_path = '/home/gaia/Documents/processing_1_sec/2020/landslide_auto_comparison.jpg'

# Vérifier si le répertoire existe, sinon le créer
save_dir = os.path.dirname(save_path)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Enregistrer la figure en format JPEG
plt.savefig(save_path, format='jpeg')

# Afficher le graphique
plt.show()

# Afficher le nombre total de 'frane' pour l'année (Auto)
total_auto_frane = result_auto['frane'].sum()
print(f"Total number of 'frane' for 2020 (Auto): {total_auto_frane}")
