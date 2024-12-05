import pandas as pd
import matplotlib.pyplot as plt
import os

# Charger et préparer les données manuelles
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Vérifier la présence des colonnes nécessaires
if 'Date' not in manual_data.columns or 'frane' not in manual_data.columns:
    raise ValueError("The columns 'Date' and/or 'frane' are missing in the file '2020_manual.csv'.")

manual_data['Date'] = pd.to_datetime(manual_data['Date'])
manual_data.set_index('Date', inplace=True)
manual_data['frane_rolling'] = manual_data['frane'].rolling(window=7).mean()

# Charger et préparer les données stre/stra filtrées
stre_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_stre_stra/all_peaks.csv'
stre_data = pd.read_csv(stre_file_path)

if 'RSAM_E' not in stre_data.columns or 'Ratio' not in stre_data.columns or 'Peak_Time_UTC' not in stre_data.columns:
    raise ValueError("The necessary columns are missing in the stre/stra data.")

stre_filtered = stre_data[(stre_data['RSAM_E'] > 875) & (stre_data['Ratio'] < 6.5)]
stre_filtered['Date'] = pd.to_datetime(stre_filtered['Peak_Time_UTC']).dt.date
stre_daily_counts = stre_filtered['Date'].value_counts().sort_index()

stre_result = pd.DataFrame({
    'Date': pd.to_datetime(stre_daily_counts.index),
    'frane': stre_daily_counts.values
}).set_index('Date')
stre_result['frane_rolling'] = stre_result['frane'].rolling(window=7).mean()

# Charger et préparer les données strg/stra filtrées
strg_file_path = '/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stra/strg_stra_all_peaks_data.csv'
strg_data = pd.read_csv(strg_file_path)

if 'RSAM_G' not in strg_data.columns or 'Ratio' not in strg_data.columns or 'Peak_Time_UTC' not in strg_data.columns:
    raise ValueError("The necessary columns are missing in the strg/stra data.")

strg_filtered = strg_data[(strg_data['RSAM_G'] > 150) & (strg_data['Ratio'] < 2.5)]
strg_filtered['Date'] = pd.to_datetime(strg_filtered['Peak_Time_UTC']).dt.date
strg_daily_counts = strg_filtered['Date'].value_counts().sort_index()

strg_result = pd.DataFrame({
    'Date': pd.to_datetime(strg_daily_counts.index),
    'frane': strg_daily_counts.values
}).set_index('Date')
strg_result['frane_rolling'] = strg_result['frane'].rolling(window=7).mean()

# Tracer les trois courbes
plt.figure(figsize=(12, 8))

plt.plot(manual_data.index, manual_data['frane_rolling'], label='2020 Manual - Weekly Average', color='blue', linewidth=2)
plt.plot(stre_result.index, stre_result['frane_rolling'], label='2020 Stre/stra Filtered - Weekly Average', color='orange', linewidth=2)
plt.plot(strg_result.index, strg_result['frane_rolling'], label='2020 Strg/stra Filtered - Weekly Average', color='green', linewidth=2)

# Ajouter un titre et des légendes
title = 'Comparison of Landslide Detections (Weekly Average)\nManual vs Filtered Data'
plt.title(title)
plt.xlabel('Date')
plt.ylabel('Number of Landslides (Frane)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Afficher le graphique
plt.show()

# Calculer et afficher le nombre total de frane pour chaque dataset
total_manual_frane = manual_data['frane'].sum()
total_stre_frane = stre_result['frane'].sum()
total_strg_frane = strg_result['frane'].sum()

print(f"Total number of 'frane' for 2020 (Manual): {total_manual_frane}")
print(f"Total number of 'frane' for 2020 (Stre/stra Filtered): {total_stre_frane}")
print(f"Total number of 'frane' for 2020 (Strg/stra Filtered): {total_strg_frane}")
