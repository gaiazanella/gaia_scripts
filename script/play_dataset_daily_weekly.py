import pandas as pd
import matplotlib.pyplot as plt

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

# Distribution statistique des 'Durations'
duration_stats = filtered_data['Duration'].describe()
median_duration = filtered_data['Duration'].median()
quartiles = filtered_data['Duration'].quantile([0.25, 0.5, 0.75])

# Première figure : les 4 premiers plots
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

# 1er subplot : nombre de glissements par jour (auto + manual)
axs[0].plot(result_auto['Date'], result_auto['frane_rolling'], label='Weekly Average (Auto)', color='orange', linewidth=2)
axs[0].plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='Weekly Average (Manual)', color='blue', linewidth=2)
axs[0].set_ylabel('Number of Landslides')
axs[0].legend()
axs[0].grid(True)

# 2ème subplot : durée moyenne quotidienne des glissements (auto)
axs[1].plot(daily_duration_mean.index, daily_duration_mean.values, label='Daily Average Duration (Auto)', color='green', linewidth=2)
axs[1].plot(daily_duration_mean_rolling.index, daily_duration_mean_rolling.values, label='Weekly Average Duration (Auto)', color='lime', linewidth=2)
axs[1].set_ylabel('Average Duration (s)')
axs[1].legend()
axs[1].grid(True)

# 3ème subplot : durée maximale quotidienne des glissements (auto)
axs[2].plot(daily_duration_max.index, daily_duration_max.values, label='Daily Max Duration (Auto)', color='red', linewidth=2)
axs[2].plot(daily_duration_max_rolling.index, daily_duration_max_rolling.values, label='Weekly Max Duration (Auto)', color='darkred', linewidth=2)
axs[2].set_ylabel('Max Duration (s)')
axs[2].legend()
axs[2].grid(True)

# 4ème subplot : RSAM_E moyen quotidien (auto)
axs[3].plot(daily_rsam_mean.index, daily_rsam_mean.values, label='Daily Average RSAM_E (Auto)', color='skyblue', linewidth=2)
axs[3].plot(daily_rsam_mean_rolling.index, daily_rsam_mean_rolling.values, label='Weekly Average RSAM_E (Auto)', color='darkblue', linewidth=2)
axs[3].set_ylabel('Average RSAM_E')
axs[3].set_xlabel('Date')
axs[3].legend()
axs[3].grid(True)

# Ajuster la mise en page
plt.tight_layout()

# Afficher la première figure
plt.show()

# Deuxième figure : distribution statistique des 'Durations'
plt.figure(figsize=(10, 6))
plt.hist(filtered_data['Duration'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.xlabel('Durations (s)')
plt.ylabel('Count')
plt.title(f'Duration Distribution\nMean={duration_stats["mean"]:.2f}, Median={median_duration:.2f}, Std={duration_stats["std"]:.2f}')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Afficher la deuxième figure
plt.show()

# Impression des statistiques
print("Statistical Distribution of 'Durations':")
print(f"Mean: {duration_stats['mean']:.2f}")
print(f"Median: {median_duration:.2f}")
print(f"Min: {duration_stats['min']:.2f}")
print(f"Max: {duration_stats['max']:.2f}")
print(f"1st Quartile: {quartiles[0.25]:.2f}")
print(f"3rd Quartile: {quartiles[0.75]:.2f}")
