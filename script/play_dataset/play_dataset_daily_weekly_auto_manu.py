import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier 'all_peaks.csv' pour 'auto'
file_path = '/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra_test/stre_stra_all_peaks_data.csv'
data = pd.read_csv(file_path)

# Filtrer les données en fonction des critères 'RSAM_E > 875' et 'Ratio < 6.5'
filtered_data = data[(data['RSAM_E'] > 875) & (data['Ratio'] < 6.5)]

# Extraire la date sans l'heure de la colonne 'Peak_Time_UTC'
filtered_data.loc[:, 'Date'] = pd.to_datetime(filtered_data['Peak_Time_UTC']).dt.date

# Compter les occurrences par jour pour 'auto' dans 'frane'
daily_counts = filtered_data['Date'].value_counts().sort_index()

# Créer un DataFrame pour les résultats 'auto'
result_auto = pd.DataFrame({
    'Date': pd.to_datetime(daily_counts.index),
    'frane': daily_counts.values
}).sort_values('Date')

# Calculer la moyenne mobile sur 7 jours pour les données 'auto'
result_auto['frane_rolling'] = result_auto['frane'].rolling(window=7).mean()

# Charger le fichier '2020_manual.csv' pour 'manual' sans appliquer les critères de sélection
manual_file_path = '/home/gaia/Documents/2020_manual.csv'
manual_data = pd.read_csv(manual_file_path)

# Extraire la date sans l'heure de la colonne 'Date' pour 'manual'
manual_data['Date'] = pd.to_datetime(manual_data['Date'])

# Calculer les occurrences quotidiennes pour 'manual'
manual_daily_counts = manual_data.groupby('Date')['frane'].sum()

# Calculer la moyenne mobile sur 7 jours pour les données 'manual'
manual_daily_counts_rolling = manual_daily_counts.rolling(window=7).mean()

# Charger le fichier CSV supplémentaire avec les dates et heures pour les lignes verticales
lines_file_path = '/home/gaia/Documents/communicati_2020_ingv_frane.csv'

# Charger le fichier CSV en spécifiant le séparateur ';' et sans en-têtes
lines_data = pd.read_csv(lines_file_path, sep=';', header=None, names=['Date', 'Time', 'Extra'])

# Convertir les dates et heures en datetime
lines_data['Datetime'] = pd.to_datetime(lines_data['Date'] + ' ' + lines_data['Time'], format='%d/%m/%Y %H:%M')

# Première figure : uniquement le premier subplot
plt.figure(figsize=(10, 6))

# 1er subplot : nombre de glissements par jour (auto + manual)
plt.plot(result_auto['Date'], result_auto['frane_rolling'], label='7-Day Rolling Average (Auto)', color='blue', linewidth=2)
plt.plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='7-Day Rolling Average (Manual)', color='orange', linewidth=2)
plt.plot(result_auto['Date'], result_auto['frane'], label='Daily Count (Auto)', color='blue', linestyle='--', linewidth=2)
plt.plot(manual_daily_counts.index, manual_daily_counts.values, label='Daily Count (Manual)', color='orange', linestyle='--', linewidth=2)

# Ajouter des lignes verticales noires pour chaque date et heure dans le fichier 'lines_data'
first_line = True  # Booléen pour savoir si c'est la première ligne verticale
for line in lines_data['Datetime']:
    if first_line:
        plt.axvline(x=line, color='black', linewidth=2, label='lava flow')  # Premier label
        first_line = False
    else:
        plt.axvline(x=line, color='black', linewidth=2)  # Pas de label pour les lignes suivantes

plt.ylabel('Rockfall Rate (N/day)')
plt.legend()
plt.grid(True)

# Afficher la première figure
plt.tight_layout()
plt.show()

# Deuxième figure avec deux subplots en colonne (1 et 2), partageant les axes X et Y
fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True, sharey=True)

# Subplot 1 : Moyenne mobile sur 7 jours pour Auto et Manual
axs[0].plot(result_auto['Date'], result_auto['frane_rolling'], label='7-Day Rolling Average (Auto)', color='blue', linewidth=2)
axs[0].plot(manual_daily_counts_rolling.index, manual_daily_counts_rolling.values, label='7-Day Rolling Average (Manual)', color='orange', linewidth=2)
axs[0].set_title('7-Day Rolling Average (Auto vs Manual)')
axs[0].set_ylabel('Rockfall Rate (N/day)')
axs[0].legend()
axs[0].grid(True)

# Ajouter des lignes verticales noires pour chaque date et heure dans le fichier 'lines_data' au premier subplot
for line in lines_data['Datetime']:
    axs[0].axvline(x=line, color='black', linewidth=2)

# Subplot 2 : Nombre quotidien de glissements pour Auto et Manual (sans moyenne mobile)
axs[1].plot(result_auto['Date'], result_auto['frane'], label='Daily Count (Auto)', color='blue', linestyle='--', linewidth=2)
axs[1].plot(manual_daily_counts.index, manual_daily_counts.values, label='Daily Count (Manual)', color='orange', linestyle='--', linewidth=2)
axs[1].set_title('Daily Landslides (Auto vs Manual)')
axs[1].set_ylabel('Rockfall Rate (N/day)')
axs[1].legend()
axs[1].grid(True)

# Ajouter des lignes verticales noires pour chaque date et heure dans le fichier 'lines_data' au deuxième subplot
for line in lines_data['Datetime']:
    axs[1].axvline(x=line, color='black', linewidth=2)

# Afficher la deuxième figure avec les axes synchronisés
plt.tight_layout()
plt.show()
