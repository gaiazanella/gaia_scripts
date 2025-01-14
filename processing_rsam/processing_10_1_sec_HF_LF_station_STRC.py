###PACKAGES
import obspy
from obspy import read, UTCDateTime
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.filter import bandpass, envelope
from obspy.core.trace import Trace
from matplotlib.dates import DateFormatter
import pandas as pd
from obspy.clients.filesystem.sds import Client
from obspy.signal.trigger import plot_trigger
import datetime as dt
from datetime import datetime, timedelta
from obspy.core import Stream
import os

###############
###SMOOTH SIGNAL
def smooth(signal, window_size):
    """
    Smooth a signal using a rolling average window.
    
    Args:
        signal: NumPy array, the input signal to be smoothed.
        window_size: int, the size of the rolling window in samples.
        
    Returns:
        smoothed_signal: NumPy array, the smoothed signal.
    """
    window = np.ones(window_size) / window_size  # crée un tableau rempli de 1 de taille égale à window_size ; chaque case devient 1/window_size : moyenne uniforme
    smoothed_signal = np.convolve(signal, window, mode='same')  #convolution entre le signal et la fentre de lissage ; same garantit que le signal lissé aura la même longueur que le signal d'origine
    return smoothed_signal

win = 60  # 60 secondes
fs = 50  # 50 Hz
samples = win * fs

# Initialise dates using datetime
t_init = UTCDateTime("2020-01-01T00:00:00")
t_end = UTCDateTime("2021-01-01T00:00:00")
save_dir = '/home/gaia/Documents/processing_1_sec/2020/rsam/'
db = '/mnt/bigmama3/miniseed'
stz = ['STRC']  # Liste des stations à traiter (maintenant seulement STRG)
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']

fminb3 = 1
fmaxb3 = 8
fminb4 = 8
fmaxb4 = 15

# Create a sequence of time values spaced one day apart between t_init and t_end 
th_day = []
current_time = t_init
while current_time <= t_end:
    th_day.append(current_time)
    current_time += timedelta(days=1)

client = Client(db)

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for j in range(len(stz)):  # Cette boucle sera maintenant exécutée une seule fois, car stz ne contient que 'STRG'
    print(f"Processing station: {stz[j]}")  # Affichage du nom de la station en cours
    for i in range(len(th_day) - 1): 
        stb3 = client.get_waveforms(network='*', station=stz[j], location="", channel=channel[0], 
                                    starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))
        stb4 = client.get_waveforms(network='*', station=stz[j], location="", channel=channel[0], 
                                    starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))

        # Debug : vérifier si les données sont récupérées
        print(f"Retrieved {len(stb3)} traces for {stz[j]} on {th_day[i]} for B3.")
        print(f"Retrieved {len(stb4)} traces for {stz[j]} on {th_day[i]} for B4.")

        # Vérification si des données ont été récupérées
        if len(stb3) == 0:
            print(f"No data for {stz[j]} on {th_day[i]} for B3.")
            continue  # Si aucune donnée pour B3, passer au suivant

        if len(stb4) == 0:
            print(f"No data for {stz[j]} on {th_day[i]} for B4.")
            continue  # Si aucune donnée pour B4, passer au suivant

        # Traitement pour B3
        stb3.merge(fill_value='interpolate')
        stb3.detrend("demean")  # met le signal autour de zéro
        stb3.detrend("linear")  # enlève la pente
        stb3.filter('bandpass', freqmin=fminb3, freqmax=fmaxb3)  # Filtrage de B3
        s_envb3 = obspy.signal.filter.envelope(stb3[0].data)
        s_env_smoothb3 = smooth(s_envb3, samples)

        # Traitement pour B4
        stb4.merge(fill_value='interpolate')
        stb4.detrend("demean")  # met le signal autour de zéro
        stb4.detrend("linear")  # enlève la pente
        stb4.filter('bandpass', freqmin=fminb4, freqmax=fmaxb4)  # Filtrage de B4
        s_envb4 = obspy.signal.filter.envelope(stb4[0].data)
        s_env_smoothb4 = smooth(s_envb4, samples)

        # Paramètres pour le calcul de la moyenne
        sampling_rate = stb3[0].stats.sampling_rate  # Taux d'échantillonnage
        start_time = UTCDateTime(stb3[0].stats.starttime.date)  # 00:00:00 du jour actuel
        end_time = start_time + 86400  # 86400 secondes = 24 heures
        results = []

        # Parcourir chaque multiple de 10 secondes de la période
        current_time = start_time 
        while current_time < end_time:
            window_start = current_time - 0.5  # 5 secondes avant la seconde exacte
            window_end = current_time + 0.5  # 5 secondes après la seconde exacte
            
            start_index = int((window_start - stb3[0].stats.starttime) * sampling_rate)
            end_index = int((window_end - stb3[0].stats.starttime) * sampling_rate)

            # Si l'index est valide, extraire les données pour cette fenêtre
            if 0 <= start_index < len(stb3[0].data) and 0 <= end_index <= len(stb3[0].data):
                window_datab3 = s_env_smoothb3[start_index:end_index]
                if len(window_datab3) == 1 * sampling_rate:
                    mean_valueb3 = np.mean(window_datab3)  # Calcul de la moyenne
                else:
                    mean_valueb3 = np.nan  # Incomplet => NaN
            else:
                mean_valueb3 = np.nan  # Données manquantes ou indices invalides

            if 0 <= start_index < len(stb4[0].data) and 0 <= end_index <= len(stb4[0].data):
                window_datab4 = s_env_smoothb4[start_index:end_index]
                if len(window_datab4) == 1 * sampling_rate:
                    mean_valueb4 = np.mean(window_datab4)  # Calcul de la moyenne
                else:
                    mean_valueb4 = np.nan  # Incomplet => NaN
            else:
                mean_valueb4 = np.nan  # Données manquantes ou indices invalides

            results.append((current_time, mean_valueb3, mean_valueb4))
            current_time += 1  # Incrémenter de 10 secondes

        # Séparer les temps et les moyennes
        times = [entry[0].datetime for entry in results]
        meansb3 = [entry[1] for entry in results]
        meansb4 = [entry[2] for entry in results]

        ### CREATING MY CSV FILE
        df = pd.DataFrame()
        df['time_UTC'] = times
        df['RSAM_env_smooth_1-8Hz'] = meansb3
        df['RSAM_env_smooth_8-15Hz'] = meansb4

        csv_filename = os.path.join(save_dir, f'rsam_{stz[j]}_{th_day[i].strftime("%Y%m%d")}.csv')
        df.to_csv(csv_filename, index=False)
        print(f'My file name is: {csv_filename}')
