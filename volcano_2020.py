import pandas as pd

# Créer un dictionnaire avec les données
data = {
    'Date': ['18/01/2020','19/01/2020', '19/01/2020', '03/02/2020', '03/02/2020', '28/03/2020', '29/03/2020', '31/03/2020', '01/04/2020', '15/04/2020', '16/04/2020', '19/04/2020', '19/04/2020', '19/07/2020', '13/08/2020', '10/11/2020','16/11/2020'],
    'Time_UTC': [ '22:40',
'00:30',
'10:12',
'07:59',
'19:40',
'17:00',
'04:50',
'02:10',
'08:20',
'07:46',
'07:56',
'19:52',
'23:55',
'06:27',
'14:50',
'21:04',
'09:17'],
    'Event': ['T_start',
'T_start',
'T_end',
'T_start',
'T_end',
'T_start',
'T_end',
'T_start',
'T_end',
'T_start',
'T_end',
'T_start',
'T_end',
'exp',
'exp',
'exp',
'exp']
}

# Convertir le dictionnaire en DataFrame
df = pd.DataFrame(data)

# Enregistrer le DataFrame dans un fichier CSV
output_file = '/home/gaia/Documents/volcano_2020.csv'  # Remplace le chemin par ton propre emplacement
df.to_csv(output_file, index=False)

print(f"Le fichier CSV a été créé avec succès et enregistré à {output_file}")
print(df)
