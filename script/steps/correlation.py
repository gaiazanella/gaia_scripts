import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Chargement des données
manual_data = pd.read_csv('/home/gaia/Documents/2020_manual.csv')
automatic_data = pd.read_csv('/home/gaia/Documents/processing_1_sec/2020/double_duration_speed_strg_stre/strg_stre_all_peaks_data.csv')
#automatic_data = pd.read_csv('/home/gaia/Documents/processing_10_sec/2020/dataset_durations/all_peaks.csv')
#automatic_data = pd.read_csv('/home/gaia/Documents/processing_1_sec/2020/double_duration_speed/all_peaks.csv')

# Conversion de Peak_Time_UTC en datetime et extraction de la date
automatic_data['Peak_Time_UTC'] = pd.to_datetime(automatic_data['Peak_Time_UTC'])
automatic_data['Date'] = automatic_data['Peak_Time_UTC'].dt.date

# Ajout de la colonne 'Date' dans les données manuelles
manual_data['Date'] = pd.to_datetime(manual_data['Date']).dt.date

# Définition des seuils
ratio_thresholds = np.arange(3, 10, 1)  # Seuils de ratio de 3 à 9
rsam_thresholds = np.arange(700, 1100, 50)  # Seuils RSAM de 700 à 1000

# Création d'un DataFrame pour stocker les corrélations
correlation_df = pd.DataFrame(index=rsam_thresholds, columns=ratio_thresholds)

# Calcul de la corrélation pour chaque combinaison de seuils
for ratio_seuil in ratio_thresholds:
    for rsam_seuil in rsam_thresholds:
        # Filtrer les détections automatiques
        filtred_detections = automatic_data[
            (automatic_data['Ratio'] < ratio_seuil) & 
            (automatic_data['RSAM_E'] > rsam_seuil)
        ]
        
        # Comptage des détections par jour
        daily_detections = filtred_detections.groupby('Date').size().reindex(manual_data['Date'], fill_value=0)

        # Vérification des données avant le calcul de la corrélation
        if daily_detections.nunique() > 1 and manual_data['frane'].nunique() > 1:
            correlation, _ = pearsonr(manual_data['frane'], daily_detections)
        else:
            correlation = np.nan
            
        # Stocker la corrélation
        correlation_df.loc[rsam_seuil, ratio_seuil] = correlation

# Conversion des valeurs en numériques
correlation_df = correlation_df.apply(pd.to_numeric)
print(np.max(correlation_df))

# Diagnostic : Visualisation des données
print("Données manuelles (échantillon) :")
print(manual_data.head())
print("\nDonnées automatiques (échantillon) :")
print(automatic_data.head())
print("\nCarte de chaleur des corrélations :")
print(correlation_df)

# Visualisation de la carte de chaleur des corrélations
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_df, annot=True, cmap='coolwarm', cbar_kws={'label': 'Pearson Correlation'})
#sns.heatmap(correlation_df, annot=True, cmap='coolwarm', cbar_kws={'label': 'Pearson Correlation'}, vmin=-1, vmax=1)
plt.xlabel('Ratio Thresholds')
plt.ylabel('RSAM(E) Thresholds')

# Inverser l'axe Y
plt.gca().invert_yaxis()  # Inverser l'axe des ordonnées

plt.show()
