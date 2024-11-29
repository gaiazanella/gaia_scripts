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
import obspy
from obspy.signal.filter import bandpass, envelope
from obspy import signal, read, UTCDateTime
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
    window = np.ones(window_size) / window_size # crée un tableau rempli de 1 de taille égale à window_size ; chaque case devient 1/window_size : moyenne uniforme
    smoothed_signal = np.convolve(signal, window, mode='same') #convolution entre le signal et la fentre de lissage ; same garantit que le signal lissé aura la même longueur que le signal d'origine
    # La convolution est calculée en "faisant glisser" la fenêtre le long du signal et en prenant la moyenne des valeurs sous la fenêtre à chaque étape
    return smoothed_signal

win = 60 #60 #window of 60 seconds, 1 min
fs=50 #50 Hz
samples = win*fs

# Initialise dates using datetime
t_init=UTCDateTime("2024-01-01T00:00:00")
t_end=UTCDateTime("2024-10-01T00:00:00")
save_dir = '/home/gaia/Documents/processing_1_sec/2024/rsam/'
db='/mnt/bigmama3/miniseed'
stz = ['STRA', 'STRE']
net = ['IT', 'IT']
channel = ['EHZ', 'EHZ']

fminb3=1
fmaxb3=8
fminb4=8
fmaxb4=15

# Create a sequence of time values spaced one day apart between t_init and t_end 
th_day = []
current_time = t_init
while current_time <= t_end:
    th_day.append(current_time)
    current_time += timedelta(days=1)

client = Client(db)

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for j in range (len(stz)) :
    for i in range (len(th_day)-1): 
        stb3 = client.get_waveforms(network='*', station=stz[j], location = "", channel=channel[0], starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))
        print(stb3)
        stb4 = client.get_waveforms(network='*', station=stz[j], location = "", channel=channel[0], starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))
        print(stb4)

############################### B3
        #Empty trace check
        if len(stb3) ==0:
            print('trace vide')
            continue
        trb3 = stb3[0]  # Assumant qu'il n'y a qu'un Trace

        # Check sampling rates and resample if necessary
        for traceb3 in stb3:
            # Ensure the trace has the correct sampling rate
            if traceb3.stats.sampling_rate != fs:
                print(f'Resampling trace for {stz[j]} on {th_day[i]} from {traceb3.stats.sampling_rate} Hz to {fs} Hz.')
                # Resample the trace to the desired sampling rate
                traceb3.resample(fs)

            # Check data types and convert if necessary
            if traceb3.data.dtype != np.float32:
                print(f'Converting trace data type for {stz[j]} on {th_day[i]} from {traceb3.data.dtype} to float32.')
                traceb3.data = traceb3.data.astype(np.float32)  # Convert to float32

        # Now that all traces are at the same sampling rate and data type, we can merge
        try:
            stb3.merge(fill_value='interpolate')  # Merge traces, filling gaps with interpolation
            print(f'Merged traces for {stz[j]} on {th_day[i]} successfully.')
        except Exception as e:
            print(f'Error merging traces for {stz[j]} on {th_day[i]}: {e}')

        sb3=stb3[0].data
        stb3.merge(fill_value='interpolate') #création d'une valeur estimée en fonction des valeurs avant et apres l'intervalle manquant 
        sb3graph=stb3[0].data
        stb3.detrend("demean") #met le signal autour de zéro 
        stb3.detrend("linear") # enlève la pente ;  se concentre sur la variation vraie du signal 
        stb3.filter('bandpass',freqmin=fminb3,freqmax=fmaxb3) 
        tr_b3=stb3[0]
        s_envb3=stb3[0].data
        s_filtb3 = stb3[0].data
        s_envb3 = obspy.signal.filter.envelope(stb3[0].data) # met en évidence les changements d'amplitude plur lents ; courbe lisse qui suit les points max locaux
        s_env_smoothb3 = smooth(s_envb3, samples)

############################### B4
        #Empty trace check
        if len(stb4) ==0:
            print('trace vide')
            continue
        trb4 = stb4[0]  # Assumant qu'il n'y a qu'un Trace

        # Check sampling rates and resample if necessary
        for traceb4 in stb4:
            # Ensure the trace has the correct sampling rate
            if traceb4.stats.sampling_rate != fs:
                print(f'Resampling trace for {stz[j]} on {th_day[i]} from {traceb4.stats.sampling_rate} Hz to {fs} Hz.')
                # Resample the trace to the desired sampling rate
                traceb4.resample(fs)

            # Check data types and convert if necessary
            if traceb4.data.dtype != np.float32:
                print(f'Converting trace data type for {stz[j]} on {th_day[i]} from {traceb4.data.dtype} to float32.')
                traceb4.data = traceb4.data.astype(np.float32)  # Convert to float32

        # Now that all traces are at the same sampling rate and data type, we can merge
        try:
            stb3.merge(fill_value='interpolate')  # Merge traces, filling gaps with interpolation
            print(f'Merged traces for {stz[j]} on {th_day[i]} successfully.')
        except Exception as e:
            print(f'Error merging traces for {stz[j]} on {th_day[i]}: {e}')


        sb4=stb4[0].data
        stb4.merge(fill_value='interpolate')
        sb4graph=stb4[0].data
        stb4.detrend("demean")
        stb4.detrend("linear")
        stb4.filter('bandpass',freqmin=fminb4,freqmax=fmaxb4) 
        tr_b4=stb4[0]
        s_envb4=stb4[0].data
        s_filtb4 = stb4[0].data
        s_envb4 = obspy.signal.filter.envelope(stb4[0].data)
        s_env_smoothb4 = smooth(s_envb4, samples)

# Paramètres pour le calcul de la moyenne
        sampling_rate = trb3.stats.sampling_rate  # Taux d'échantillonnage

# Définir la période d'analyse, de minuit à minuit du jour suivant
        start_time = UTCDateTime(trb3.stats.starttime.date)  # 00:00:00 du jour actuel
        end_time = start_time + 86400  # 86400 secondes = 24 heures

# Créer une liste pour stocker les résultats (temps, moyenne)
        results = []

# Parcourir chaque multiple de 10 secondes de la période
        current_time = start_time 
        while current_time < end_time:
    # Fenêtre de 5 secondes avant et 5 secondes après (10 secondes en tout)
            window_start = current_time - 0.5  # 5 secondes avant la seconde exacte
            window_end = current_time + 0.5  # 5 secondes après la seconde exacte
    
    # Trouver les indices correspondant à cette fenêtre de 10 secondes
            start_index = int((window_start - tr_b3.stats.starttime) * sampling_rate)
            end_index = int((window_end - tr_b3.stats.starttime) * sampling_rate)
############################### B3
    # Si l'index est valide, extraire les données pour cette fenêtre
            if 0 <= start_index < len(tr_b3.data) and 0 <= end_index <= len(tr_b3.data):
                window_datab3 = s_env_smoothb3[start_index:end_index]
        
        # Si la fenêtre est complète (exactement 10 secondes de données)
                if len(window_datab3) == 1 * sampling_rate:
                    mean_valueb3 = np.mean(window_datab3)  # Calcul de la moyenne
                else:
                    mean_valueb3 = np.nan  # Incomplet => NaN
            else:
                mean_valueb3 = np.nan  # Données manquantes ou indices invalides
############################### B4
    # Si l'index est valide, extraire les données pour cette fenêtre
            if 0 <= start_index < len(tr_b4.data) and 0 <= end_index <= len(tr_b4.data):
                window_datab4 = s_env_smoothb4[start_index:end_index]
        
        # Si la fenêtre est complète (exactement 10 secondes de données)
                if len(window_datab4) == 1 * sampling_rate:
                    mean_valueb4 = np.mean(window_datab4)  # Calcul de la moyenne
                else:
                    mean_valueb4 = np.nan  # Incomplet => NaN
            else:
                mean_valueb4 = np.nan  # Données manquantes ou indices invalides


    # Ajouter le temps rond (multiples de 10 secondes) et la moyenne à la liste des résultats
            results.append((current_time, mean_valueb3, mean_valueb4))

    # Passer au prochain multiple de 10 secondes
            current_time += 1  # Incrémenter de 10 secondes

# Séparer les temps et les moyennes
        times = [entry[0].datetime for entry in results]  # Convertir UTCDateTime en datetime
        meansb3 = [entry[1] for entry in results]  # Extraire les moyennes
        meansb4 = [entry[2] for entry in results]

            ### CREATING MY CSV FILE
        df = pd.DataFrame()
    #df['time'] = t
        df['time_UTC'] = times
        df['RSAM_env_smooth_1-8Hz'] = meansb3
        df['RSAM_env_smooth_8-15Hz'] = meansb4

        csv_filename = os.path.join(save_dir, f'rsam_{stz[j]}_{th_day[i].strftime("%Y%m%d")}.csv')
        df.to_csv(csv_filename, index=False)
        print(f'mon nom de fichier est ', csv_filename)

# Créer le graphique avec deux tracés
        #plt.figure(figsize=(12, 6))

# Tracer la trace normale
        #trace_times = [trb4.stats.starttime + i / sampling_rate for i in range(len(trb4.data))]  # Temps pour la trace normale
        #trace_times = [t.datetime for t in trace_times]  # Convertir UTCDateTime en datetime
        #starttime = UTCDateTime(stb4[0].stats.starttime).datetime
        #time = pd.to_datetime(starttime + pd.to_timedelta(np.arange(0, len(sb4graph) / (fs), 1 / fs), unit='S'))
        #plt.plot(time, sb4graph, label="Trace", color='yellow', alpha=0.6)
        #plt.plot(time, s_filtb4, label="Filtered 8-15Hz", color='blue', alpha=0.6)
        #plt.plot(time, s_envb4, label="Filtered Envelope 8-15Hz", color='green', alpha=0.6)
        #plt.plot(time, s_env_smoothb4, label="Filtered Envelope Smooth 8-15Hz", color='purple', alpha=0.6)
        #plt.plot(df['time_UTC'],df['RSAM_env_smooth_8-15Hz'],label='Filtered Envelope Smooth Window 10 s',color='red')

# Ajout des labels et du titre
        #plt.xlabel('Time (UTC)',fontsize=18)
        #plt.ylabel('RSAM (counts)',fontsize=18)
        #plt.xticks(rotation=45)  # Rotation de l'axe des X pour une meilleure lisibilité
        #plt.grid(True)
        #plt.xticks(fontsize=18)
        #plt.yticks(fontsize=18)

# Légende
        #plt.legend(fontsize=18)

# Afficher le graphique
        #plt.tight_layout()
        #plt.show()
