import pandas as pd
import matplotlib.pyplot as plt
import os

# Charger le fichier '2020_manual.csv' contenant les détections manuelles
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Vérifiez que les colonnes nécessaires existent dans le fichier
if 'Date' not in manual_data.columns or 'frane' not in manual_data.columns:
    raise ValueError("The columns 'Date' and/or 'frane' are missing in the file '2020_manual.csv'.")

# Convertir la colonne 'Date' en datetime pour s'assurer de la cohérence
manual_data['Date'] = pd.to_datetime(manual_data['Date'])

# Compter les occurrences de 'frane' par jour
daily_counts_manual = manual_data.groupby('Date')['frane'].sum()

# Calculer la moyenne mobile hebdomadaire des données manuelles
manual_data.set_index('Date', inplace=True)
manual_data['frane_rolling'] = manual_data['frane'].rolling(window=7).mean()

# Tracer le graphique
plt.figure(figsize=(14, 10))  # Agrandir la figure

# Tracer les données journalières
plt.plot(daily_counts_manual.index, daily_counts_manual.values, label='Daily Counts', color='lightgray', linestyle='-', linewidth=2)

# Tracer les données lissées sur 7 jours
plt.plot(manual_data.index, manual_data['frane_rolling'], label='Weekly Smoothed', color='gray', linestyle='-', linewidth=3)

# Configurer le graphique
plt.ylabel('Landslide Event Rate', fontsize=20)
plt.xlabel('Date', fontsize=20)
plt.grid(True)
plt.xticks(rotation=45, fontsize=16)  # Rotation des dates et taille de police pour les ticks de l'axe X
plt.yticks(fontsize=16)  # Taille de police pour les ticks de l'axe Y
plt.legend(fontsize=16)
plt.tight_layout()

# Définir le chemin d'enregistrement de l'image
save_path = '/home/gaia/Documents/processing_1_sec/2020/landslide_comparison_manual_smoothed_vs_daily.jpg'

# Vérifier si le répertoire existe, sinon le créer
save_dir = os.path.dirname(save_path)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Enregistrer la figure en format JPEG
plt.savefig(save_path, format='jpeg')

# Afficher le graphique
plt.show()

# Afficher le nombre total de 'frane' pour l'année (manuelle)
total_manual_frane = manual_data['frane'].sum()
print(f"Total number of 'frane' for 2020 (Manual): {total_manual_frane}")
