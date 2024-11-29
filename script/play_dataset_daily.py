import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier 'all_peaks.csv' pour 'auto'
#file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed/all_peaks.csv'
file_path = '/home/gaia/Documents/processing_10_sec/2020/dataset_durations/all_peaks.csv'
data = pd.read_csv(file_path)

# Filtrer les données en fonction des critères 'RSAM_E > 875' et 'Ratio < 6.5'
filtered_data = data[(data['RSAM_E'] > 875) & (data['Ratio'] < 6.5)]

# Extraire la date sans l'heure de la colonne 'Peak_Time_UTC'
filtered_data['Date'] = pd.to_datetime(filtered_data['Peak_Time_UTC']).dt.date

# Compter les occurrences par jour pour 'auto' dans 'frane'
daily_counts = filtered_data['Date'].value_counts().sort_index()

# Créer un DataFrame pour les résultats 'auto'
result_auto = pd.DataFrame({
    'Date': pd.to_datetime(daily_counts.index),
    'frane': daily_counts.values
}).sort_values('Date')

# Calculer la moyenne mobile hebdomadaire pour 'frane' (subgraph 1)
result_auto['frane_rolling'] = result_auto['frane'].rolling(window=7).mean()

# Charger le fichier '2020_manual.csv' pour 'manual' sans appliquer les critères de sélection
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Extraire la date sans l'heure de la colonne 'Date' pour 'manual'
manual_data['Date'] = pd.to_datetime(manual_data['Date'])

# Calculer la moyenne mobile hebdomadaire pour 'manual' (moyenne des 'frane')
manual_daily_counts = manual_data.groupby('Date')['frane'].sum()  # On suppose qu'il faut compter les 'frane' par jour
manual_daily_counts_rolling = manual_daily_counts.rolling(window=7).mean()

# Créer un DataFrame pour les autres informations nécessaires pour 'auto' (durée, RSAM_E)
daily_duration_mean = filtered_data.groupby('Date')['Duration'].mean()
daily_duration_max = filtered_data.groupby('Date')['Duration'].max()
daily_rsam_mean = filtered_data.groupby('Date')['RSAM_E'].mean()
daily_rsam_max = filtered_data.groupby('Date')['RSAM_E'].max()

# Tracer les 5 subplots
fig, axs = plt.subplots(5, 1, figsize=(10, 15), sharex=True)  # Réduit la taille de la figure

# 1er subplot : nombre de glissements de terrain par jour (moyenne mobile hebdomadaire) - Auto + Manual
axs[0].plot(result_auto['Date'], result_auto['frane_rolling'], label='Weekly Average (Auto)', color='orange', linewidth=2)
axs[0].plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='Weekly Average (Manual)', color='blue', linewidth=2)
axs[0].set_ylabel('Number of Landslides')
axs[0].legend()
axs[0].grid(True)

# 2ème subplot : durée moyenne quotidienne des glissements de terrain (auto)
axs[1].plot(daily_duration_mean.index, daily_duration_mean.values, label='Average Daily Duration (Auto)', color='green', linewidth=2)
axs[1].set_ylabel('Average Duration (s)')
axs[1].legend()
axs[1].grid(True)

# 3ème subplot : durée maximale quotidienne des glissements de terrain (auto)
axs[2].plot(daily_duration_max.index, daily_duration_max.values, label='Max Daily Duration (Auto)', color='red', linewidth=2)
axs[2].set_ylabel('Max Duration (s)')
axs[2].legend()
axs[2].grid(True)

# 4ème subplot : valeur moyenne quotidienne de 'RSAM_E' (auto)
axs[3].plot(daily_rsam_mean.index, daily_rsam_mean.values, label='Average RSAM_E (Auto)', color='blue', linewidth=2)
axs[3].set_ylabel('Average RSAM_E')
axs[3].legend()
axs[3].grid(True)

# 5ème subplot : valeur maximale quotidienne de 'RSAM_E' (auto)
axs[4].plot(daily_rsam_max.index, daily_rsam_max.values, label='Max RSAM_E (Auto)', color='purple', linewidth=2)
axs[4].set_xlabel('Date')
axs[4].set_ylabel('Max RSAM_E')
axs[4].legend()
axs[4].grid(True)

# Rotation des dates sur l'axe x pour une meilleure lisibilité
plt.xticks(rotation=45, ha='right')  # Ajuster l'alignement des dates pour plus de lisibilité

# Ajuster la mise en page
plt.tight_layout()

# Afficher le graphique
plt.show()
