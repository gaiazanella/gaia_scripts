import pandas as pd

# Charger le fichier CSV
peaks_data = pd.read_csv("/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra_test/stre_stra_all_peaks_data.csv")

# Filtrer les données en fonction des conditions spécifiées
filtered_data = peaks_data[(peaks_data['RSAM_E'] > 875) & (peaks_data['Ratio'] < 6.5)]

# Enregistrer les données filtrées dans un nouveau fichier CSV
filtered_data.to_csv("/home/gaia/Documents/processing_10_sec/2020/double_duration_speed_stre_stra_test/stre_stra_filtered_peaks_data.csv", index=False)

print("Le fichier filtré a été enregistré sous le nom 'stre_stra_filtered_peaks_data.csv'.")
