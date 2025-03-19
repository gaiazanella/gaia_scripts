import numpy as np
import obspy
from scipy.io import savemat

# Charger le fichier MiniSEED avec obspy
st = obspy.read("/home/gaia/Documents/mseed_landslide/mseed_lds_catalog/20201006_08.55.mseed")

# Assurez-vous qu'il y a des données
if len(st) > 0:
    # Créer un dictionnaire pour contenir les données et les métadonnées
    data_dict = {}

    # Extraire les données et les métadonnées
    for i, trace in enumerate(st):
        # Nom de la station et canal
        station = trace.stats.station
        channel = trace.stats.channel
        starttime = trace.stats.starttime
        endtime = trace.stats.endtime

        # Extraire les données de la trace
        data_dict[f"trace_{i+1}_data"] = trace.data  # Données de la trace
        data_dict[f"trace_{i+1}_stats"] = {
            "station": station,
            "channel": channel,
            "starttime": starttime.isoformat(),
            "endtime": endtime.isoformat(),
            "sampling_rate": trace.stats.sampling_rate
        }

    # Enregistrer les données sous forme de fichier .mat
    savemat("/home/gaia/Documents/mseed_landslide/mseed_lds_catalog/20201006_08.55.mat", data_dict)
    print("Fichier .mat créé avec succès.")
else:
    print("Le fichier MiniSEED est vide ou n'a pas pu être chargé.")
