import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier 'all_peaks.csv' pour 'auto'
#file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed/all_peaks.csv'
file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra_test/stre_stra_all_peaks_data.csv'

dur_41 = [
    140, 160, 180, 310, 260, 230, 170, 320, 220, 290,
    140, 140, 150, 230, 230, 180, 220, 160, 220, 270,
    180, 210, 290, 130, 200, 270, 230, 150, 190, 280,
    200, 320, 250, 190, 210, 200, 230, 190, 130, 230, 240
]

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

# Deuxième figure : distribution statistique des 'Durations'
plt.figure(figsize=(12, 8))
plt.hist(filtered_data['Duration'], bins=20, color='grey', edgecolor='black', alpha=0.7)
#plt.hist(dur_41, bins=20, color='grey', edgecolor='black', alpha=0.7)
plt.xlabel('Landslide Durations (s)', fontsize=18)  # Taille de la police de l'axe X
#plt.ylabel('Count', fontsize=18)  # Taille de la police de l'axe Y
#plt.title(f'Landslide Duration Distribution\nMean={duration_stats["mean"]:.2f}, Median={median_duration:.2f}, Std={duration_stats["std"]:.2f}', fontsize=18)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xlim(0, 500)

# Afficher la deuxième figure
plt.show()

plt.figure(figsize=(12, 8))
#plt.hist(filtered_data['Duration'], bins=20, color='grey', edgecolor='black', alpha=0.7)
plt.hist(dur_41, bins=5, color='grey', edgecolor='black', alpha=0.7)
plt.xlabel('Landslide Durations (s)', fontsize=18)  # Taille de la police de l'axe X

#plt.ylabel('Count', fontsize=18)  # Taille de la police de l'axe Y
#plt.title(f'Landslide Duration Distribution\nMean={duration_stats["mean"]:.2f}, Median={median_duration:.2f}, Std={duration_stats["std"]:.2f}', fontsize=18)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xlim(0, 500)
# Afficher la deuxième figure
plt.show()

fff
# Première figure : les 4 premiers plots
fig, axs = plt.subplots(4, 1, figsize=(12, 16), sharex=True)

# 1er subplot : nombre de glissements par jour (auto + manual)
axs[0].plot(result_auto['Date'], result_auto['frane_rolling'], label='Weekly Average (Auto)', color='orange', linewidth=2)
axs[0].plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='Weekly Average (Manual)', color='blue', linewidth=2)
axs[0].set_ylabel('Number of Landslides', fontsize=18)  # Taille de la police des labels
axs[0].legend(fontsize=14)  # Taille de la police des légendes
axs[0].grid(True)
axs[0].tick_params(axis='x', labelsize=14)  # Taille de la police de l'axe X
axs[0].tick_params(axis='y', labelsize=14)  # Taille de la police de l'axe Y

# 2ème subplot : durée moyenne quotidienne des glissements (auto)
axs[1].plot(daily_duration_mean.index, daily_duration_mean.values, label='Daily Average Duration (Auto)', color='green', linewidth=2)
axs[1].plot(daily_duration_mean_rolling.index, daily_duration_mean_rolling.values, label='Weekly Average Duration (Auto)', color='lime', linewidth=2)
axs[1].set_ylabel('Average Duration (s)', fontsize=18)  # Taille de la police des labels
axs[1].legend(fontsize=14)  # Taille de la police des légendes
axs[1].grid(True)
axs[1].tick_params(axis='x', labelsize=14)  # Taille de la police de l'axe X
axs[1].tick_params(axis='y', labelsize=14)  # Taille de la police de l'axe Y

# 3ème subplot : durée maximale quotidienne des glissements (auto)
axs[2].plot(daily_duration_max.index, daily_duration_max.values, label='Daily Max Duration (Auto)', color='red', linewidth=2)
axs[2].plot(daily_duration_max_rolling.index, daily_duration_max_rolling.values, label='Weekly Max Duration (Auto)', color='darkred', linewidth=2)
axs[2].set_ylabel('Max Duration (s)', fontsize=18)  # Taille de la police des labels
axs[2].legend(fontsize=14)  # Taille de la police des légendes
axs[2].grid(True)
axs[2].tick_params(axis='x', labelsize=14)  # Taille de la police de l'axe X
axs[2].tick_params(axis='y', labelsize=14)  # Taille de la police de l'axe Y

# 4ème subplot : RSAM_E moyen quotidien (auto)
axs[3].plot(daily_rsam_mean.index, daily_rsam_mean.values, label='Daily Average RSAM_E (Auto)', color='skyblue', linewidth=2)
axs[3].plot(daily_rsam_mean_rolling.index, daily_rsam_mean_rolling.values, label='Weekly Average RSAM_E (Auto)', color='darkblue', linewidth=2)
axs[3].set_ylabel('Average RSAM_E', fontsize=18)  # Taille de la police des labels
axs[3].set_xlabel('Date', fontsize=18)  # Taille de la police de l'axe X
axs[3].legend(fontsize=14)  # Taille de la police des légendes
axs[3].grid(True)
axs[3].tick_params(axis='x', labelsize=14)  # Taille de la police de l'axe X   
axs[3].tick_params(axis='y', labelsize=14)  # Taille de la police de l'axe Y

# Ajuster la mise en page

plt.tight_layout()

# Afficher la première figure
plt.show()



# Impression des statistiques
print("Statistical Distribution of 'Durations':")
print(f"Mean: {duration_stats['mean']:.2f}")
print(f"Median: {median_duration:.2f}")
print(f"Min: {duration_stats['min']:.2f}")
print(f"Max: {duration_stats['max']:.2f}")
print(f"1st Quartile: {quartiles[0.25]:.2f}")
print(f"3rd Quartile: {quartiles[0.75]:.2f}")

param_name = 'Ratio'  # Remplace par n'importe quel nom de colonne présent dans filtered_data

# Vérifier que le paramètre existe dans les données filtrées
if param_name in filtered_data.columns:
    # Calcul des stats descriptives
    param_stats = filtered_data[param_name].describe()
    param_median = filtered_data[param_name].median()
    param_quartiles = filtered_data[param_name].quantile([0.25, 0.75])

    # Affichage de l'histogramme
    plt.figure(figsize=(12, 8))
    plt.hist(filtered_data[param_name], bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    plt.xlabel(param_name, fontsize=18)
    plt.ylabel('Count', fontsize=18)
    plt.title(f'{param_name} Distribution\nMean={param_stats["mean"]:.2f}, Median={param_median:.2f}, Std={param_stats["std"]:.2f}', fontsize=18)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Impression des statistiques
    print(f"\nStatistical Distribution of '{param_name}':")
    print(f"Mean: {param_stats['mean']:.2f}")
    print(f"Median: {param_median:.2f}")
    print(f"Min: {param_stats['min']:.2f}")
    print(f"Max: {param_stats['max']:.2f}")
    print(f"1st Quartile: {param_quartiles[0.25]:.2f}")
    print(f"3rd Quartile: {param_quartiles[0.75]:.2f}")
else:
    print(f"\nLe paramètre '{param_name}' n'existe pas dans les données filtrées.")

param_name = 'RSAM_A'
sconv1 = 3.18e-6
sconv2 = 800
sconv = sconv1 / sconv2  # ≈ 3.975e-9

if param_name in filtered_data.columns:
    transformed_param = filtered_data[param_name] * sconv

    # Stats
    param_stats = transformed_param.describe()
    param_median = transformed_param.median()
    param_quartiles = transformed_param.quantile([0.25, 0.75])

    # Histogramme
    plt.figure(figsize=(12, 8))
    plt.hist(transformed_param, bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    plt.xlabel(f'{param_name} (transformed)', fontsize=18)
    plt.ylabel('Count', fontsize=18)
    plt.title(f'{param_name} (transformed) Distribution\n'
              f'Mean={param_stats["mean"]}, Median={param_median}, Std={param_stats["std"]}', fontsize=18)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Statistiques
    print(f"\nStatistical Distribution of transformed '{param_name}':")
    print(f"Mean: {param_stats['mean']}")
    print(f"Median: {param_median}")
    print(f"Min: {param_stats['min']}")
    print(f"Max: {param_stats['max']}")
    print(f"1st Quartile: {param_quartiles[0.25]}")
    print(f"3rd Quartile: {param_quartiles[0.75]}")
else:
    print(f"\nLe paramètre '{param_name}' n'existe pas dans les données filtrées.")

param_name = 'RSAM_E'
sconv1 = 3.18e-6
sconv2 = 800
sconv = sconv1 / sconv2  # ≈ 3.975e-9

if param_name in filtered_data.columns:
    transformed_param = filtered_data[param_name] * sconv

    # Stats
    param_stats = transformed_param.describe()
    param_median = transformed_param.median()
    param_quartiles = transformed_param.quantile([0.25, 0.75])

    # Histogramme
    plt.figure(figsize=(12, 8))
    plt.hist(transformed_param, bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    plt.xlabel(f'{param_name} (transformed)', fontsize=18)
    plt.ylabel('Count', fontsize=18)
    plt.title(f'{param_name} (transformed) Distribution\n'
              f'Mean={param_stats["mean"]}, Median={param_median}, Std={param_stats["std"]}', fontsize=18)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Statistiques
    print(f"\nStatistical Distribution of transformed '{param_name}':")
    print(f"Mean: {param_stats['mean']}")
    print(f"Median: {param_median}")
    print(f"Min: {param_stats['min']}")
    print(f"Max: {param_stats['max']}")
    print(f"1st Quartile: {param_quartiles[0.25]}")
    print(f"3rd Quartile: {param_quartiles[0.75]}")
else:
    print(f"\nLe paramètre '{param_name}' n'existe pas dans les données filtrées.")


# Conversion RSAM_A et RSAM_E
sconv1 = 3.18e-6
sconv2 = 800
sconv = sconv1 / sconv2  # ≈ 3.975e-9

# Transformation des colonnes RSAM
filtered_data['RSAM_A_transformed'] = filtered_data['RSAM_A'] * sconv
filtered_data['RSAM_E_transformed'] = filtered_data['RSAM_E'] * sconv

# Création d'une figure avec 4 sous-graphiques
fig, axs = plt.subplots(4, 1, figsize=(12, 20))

# Histogramme de Duration
axs[0].hist(filtered_data['Duration'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axs[0].set_title('Distribution of Duration', fontsize=16)
axs[0].set_xlabel('Duration (s)', fontsize=14)
axs[0].set_ylabel('Count', fontsize=14)
axs[0].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de Ratio
axs[1].hist(filtered_data['Ratio'], bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
axs[1].set_title('Distribution of Ratio', fontsize=16)
axs[1].set_xlabel('Ratio', fontsize=14)
axs[1].set_ylabel('Count', fontsize=14)
axs[1].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de RSAM_A transformé
axs[2].hist(filtered_data['RSAM_A_transformed'], bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
axs[2].set_title('Distribution of RSAM_A (transformed)', fontsize=16)
axs[2].set_xlabel('RSAM_A (m/s)', fontsize=14)
axs[2].set_ylabel('Count', fontsize=14)
axs[2].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de RSAM_E transformé
axs[3].hist(filtered_data['RSAM_E_transformed'], bins=50, color='plum', edgecolor='black', alpha=0.7)
axs[3].set_title('Distribution of RSAM_E (transformed)', fontsize=16)
axs[3].set_xlabel('RSAM_E (m/s)', fontsize=14)
axs[3].set_ylabel('Count', fontsize=14)
axs[3].grid(axis='y', linestyle='--', alpha=0.7)

# Ajustement de l'espacement
plt.tight_layout()
plt.show()


# Conversion RSAM_A et RSAM_E
sconv1 = 3.18e-6
sconv2 = 800
sconv = sconv1 / sconv2

# Transformation des colonnes RSAM
filtered_data['RSAM_A_transformed'] = filtered_data['RSAM_A'] * sconv
filtered_data['RSAM_E_transformed'] = filtered_data['RSAM_E'] * sconv

# Création de la figure avec 2 lignes et 2 colonnes
fig, axs = plt.subplots(2, 2, figsize=(16, 12))

# Histogramme de Duration
axs[0, 0].hist(filtered_data['Duration'], bins=40, color='grey', edgecolor='black', alpha=0.7)
#axs[0, 0].set_title('Distribution of Duration', fontsize=16)
axs[0, 0].set_xlabel('Duration (s)', fontsize=14)
#axs[0, 0].set_ylabel('Count', fontsize=14)
axs[0, 0].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de Ratio
axs[0, 1].hist(filtered_data['Ratio'], bins=50, color='grey', edgecolor='black', alpha=0.7)
#axs[0, 1].set_title('Distribution of Ratio', fontsize=16)
axs[0, 1].set_xlabel('Amplitude Ratio', fontsize=14)
#axs[0, 1].set_ylabel('Count', fontsize=14)
axs[0, 1].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de RSAM_A transformé
axs[1, 0].hist(filtered_data['RSAM_A_transformed'], bins=50, color='grey', edgecolor='black', alpha=0.7)
#axs[1, 0].set_title('Distribution of RSAM_A (transformed)', fontsize=16)
axs[1, 0].set_xlabel('RSAM STRA (m/s)', fontsize=14)
#axs[1, 0].set_ylabel('Count', fontsize=14)
axs[1, 0].grid(axis='y', linestyle='--', alpha=0.7)

# Histogramme de RSAM_E transformé
axs[1, 1].hist(filtered_data['RSAM_E_transformed'], bins=50, color='grey', edgecolor='black', alpha=0.7)
#axs[1, 1].set_title('Distribution of RSAM_E (transformed)', fontsize=16)
axs[1, 1].set_xlabel('RSAM STRE (m/s)', fontsize=14)
#axs[1, 1].set_ylabel('Count', fontsize=14)
axs[1, 1].grid(axis='y', linestyle='--', alpha=0.7)

# Ajustement des espacements
plt.tight_layout()
plt.show()
