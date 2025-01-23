import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Importer seaborn pour KDE
import numpy as np  # Pour les manipulations de données

# Charger le fichier 'all_peaks.csv' pour 'auto'
file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed/all_peaks.csv'
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

# Calculer la moyenne mobile hebdomadaire pour 'frane'
result_auto['frane_rolling'] = result_auto['frane'].rolling(window=7).mean()

# Charger le fichier '2020_manual.csv' pour 'manual' sans appliquer les critères de sélection
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Extraire la date sans l'heure de la colonne 'Date' pour 'manual'
manual_data['Date'] = pd.to_datetime(manual_data['Date'])

# Calculer la moyenne mobile hebdomadaire pour 'manual'
manual_daily_counts = manual_data.groupby('Date')['frane'].sum()
manual_daily_counts_rolling = manual_daily_counts.rolling(window=7).mean()

# Créer un DataFrame pour les autres informations nécessaires pour 'auto' (durée, RSAM_E)
daily_duration_mean = filtered_data.groupby('Date')['Duration'].mean()
daily_duration_max = filtered_data.groupby('Date')['Duration'].max()
daily_rsam_mean = filtered_data.groupby('Date')['RSAM_E'].mean()
daily_rsam_max = filtered_data.groupby('Date')['RSAM_E'].max()

# Appliquer la moyenne mobile hebdomadaire (7 jours) sur toutes les données
daily_duration_mean_rolling = daily_duration_mean.rolling(window=7).mean()
daily_duration_max_rolling = daily_duration_max.rolling(window=7).mean()
daily_rsam_mean_rolling = daily_rsam_mean.rolling(window=7).mean()
daily_rsam_max_rolling = daily_rsam_max.rolling(window=7).mean()

# Calcul de la moyenne quotidienne du 'Ratio' (auto)
daily_ratio_mean = filtered_data.groupby('Date')['Ratio'].mean()

# Appliquer la moyenne mobile hebdomadaire (7 jours) pour 'Ratio'
daily_ratio_mean_rolling = daily_ratio_mean.rolling(window=7).mean()

# Distribution statistique des 'Durations'
duration_stats = filtered_data['Duration'].describe()
median_duration = filtered_data['Duration'].median()
quartiles = filtered_data['Duration'].quantile([0.25, 0.5, 0.75])

# Première figure : les 5 premiers plots
fig, axs = plt.subplots(5, 1, figsize=(12, 20), sharex=True)

# 1er subplot : nombre de glissements par jour (auto + manual)
axs[0].plot(result_auto['Date'], result_auto['frane_rolling'], label='Weekly Average (Auto)', color='cyan', linewidth=2)
axs[0].plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='Weekly Average (Manual)', color='grey', linewidth=2)
axs[0].set_ylabel('Number of \nLandslides', fontsize=18)
axs[0].legend(fontsize=14)
axs[0].grid(True)
axs[0].tick_params(axis='x', labelsize=14)
axs[0].tick_params(axis='y', labelsize=14)

# 2ème subplot : durée moyenne quotidienne des glissements (auto)
axs[1].plot(daily_duration_mean.index, daily_duration_mean.values, label='Daily Average Duration (Auto)', color='green', linewidth=2)
axs[1].plot(daily_duration_mean_rolling.index, daily_duration_mean_rolling.values, label='Weekly Average Duration (Auto)', color='lime', linewidth=2)
axs[1].set_ylabel('Average \nDuration (s)', fontsize=18)
axs[1].legend(fontsize=14)
axs[1].grid(True)
axs[1].tick_params(axis='x', labelsize=14)
axs[1].tick_params(axis='y', labelsize=14)

# 3ème subplot : durée maximale quotidienne des glissements (auto)
axs[2].plot(daily_duration_max.index, daily_duration_max.values, label='Daily Max Duration (Auto)', color='red', linewidth=2)
axs[2].plot(daily_duration_max_rolling.index, daily_duration_max_rolling.values, label='Weekly Max Duration (Auto)', color='darkred', linewidth=2)
axs[2].set_ylabel('Max \nDuration (s)', fontsize=18)
axs[2].legend(fontsize=14)
axs[2].grid(True)
axs[2].tick_params(axis='x', labelsize=14)
axs[2].tick_params(axis='y', labelsize=14)

# 4ème subplot : RSAM_E moyen quotidien (auto)
axs[3].plot(daily_rsam_mean.index, daily_rsam_mean.values, label='Daily Average RSAM_E (Auto)', color='skyblue', linewidth=2)
axs[3].plot(daily_rsam_mean_rolling.index, daily_rsam_mean_rolling.values, label='Weekly Average RSAM_E (Auto)', color='darkblue', linewidth=2)
axs[3].set_ylabel('Average \nRSAM_E', fontsize=18)
axs[3].legend(fontsize=14)
axs[3].grid(True)
axs[3].tick_params(axis='x', labelsize=14)
axs[3].tick_params(axis='y', labelsize=14)

# 5ème subplot : Ratio moyen quotidien (auto)
axs[4].plot(daily_ratio_mean.index, daily_ratio_mean.values, label='Daily Average Ratio (Auto)', color='yellow', linewidth=2)
axs[4].plot(daily_ratio_mean_rolling.index, daily_ratio_mean_rolling.values, label='Weekly Average Ratio (Auto)', color='darkorange', linewidth=2)
axs[4].set_ylabel('Average \nRatio', fontsize=18)
axs[4].set_xlabel('Date', fontsize=18)
axs[4].legend(fontsize=14)
axs[4].grid(True)
axs[4].tick_params(axis='x', labelsize=14)
axs[4].tick_params(axis='y', labelsize=14)
axs[4].set_xlabel('Date', fontsize=18)

# Ajuster la mise en page
plt.tight_layout()

# Afficher la figure avec les 5 subplots
plt.show()
