###### processing.py
### INPUT : seismic data from '/mnt/bigmama3/
### processing seismic data to obtain files.csv
### OUTPUT : files .csv with 3 variables 'time_UTC', 'RSAM_env_smooth_1-8Hz', 'RSAM_env_smooth_8-15Hz'
### one file per day


### PACKAGES
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
###SMOOTH SIGNAL FUNCTION
def smooth(signal, window_size):
    """
    Smooth a signal using a rolling average window.
    
    Args: signal: NumPy array, the input signal to be smoothed. window_size: int, the size of the rolling window in samples.
        
    Returns: smoothed_signal: NumPy array, the smoothed signal.
    """
    window = np.ones(window_size) / window_size # Creates an array of ones of length window_size; each element is then divided by window_size, resulting in a uniform moving average
    smoothed_signal = np.convolve(signal, window, mode='same') # Convolution between the signal and the smoothing window; 'same' ensures that the smoothed signal has the same length as the original signal
    # the convolution is computed by sliding the window along the signal and calculating the average of the values within the window at each step.
    return smoothed_signal
###############

win = 60 # window of 60 seconds, 1 min
fs=50 # 50 Hz
samples = win*fs 

#t_init=UTCDateTime("2020-03-01T00:00:00")
#t_end=UTCDateTime("2020-04-01T00:00:00")
t_init=UTCDateTime("2020-08-01T00:00:00")
t_end=UTCDateTime("2020-09-01T00:00:00")

#save_dir = '/home/gaia/Documents/processing_10_sec/2019/rsam_test'
#save_dir = '/home/dario/Documenti/processing_10_sec/2021/rsam_test/'
save_dir = '/home/dario/Documenti/one_script/'
db = '/mnt/bigmama3'
stz = ['STR1','STRA','STRC','STRE','STRG']
net = ['I*', 'I*']
channel = ['*HZ', '*HZ']

### freq used B3(LF) & B4(HF)
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

for j in range (len(stz)) : #stations
    for i in range (len(th_day)-1): # day
        stb3 = client.get_waveforms(network=net[0], station=stz[j], location = "", channel=channel[0], starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))
        print(stb3)
        stb4 = client.get_waveforms(network=net[0], station=stz[j], location = "", channel=channel[0], starttime=UTCDateTime(th_day[i]), endtime=UTCDateTime(th_day[i+1]))
        print(stb4)

############################### B3
        # Empty trace check
        if len(stb3) ==0:
            print('empty trace')
            continue
        trb3 = stb3[0]  # Assuming there is only one Trace

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

        # Now that all traces are at the same sampling rate and data type
        ### Merge traces
        try:
            stb3.merge(fill_value='interpolate')  # Merge traces, filling gaps with interpolation
            print(f'Merged traces for {stz[j]} on {th_day[i]} successfully.')
        except Exception as e:
            print(f'Error merging traces for {stz[j]} on {th_day[i]}: {e}')

        sb3=stb3[0].data 
        sb3graph=stb3[0].data
        stb3.detrend("demean") # Centers the signal around zero 
        stb3.detrend("linear") # Removes the linear trend to focus on the "true" variations in the signal 
        stb3.filter('bandpass',freqmin=fminb3,freqmax=fmaxb3) 
        tr_b3=stb3[0]
        s_envb3=stb3[0].data
        s_filtb3 = stb3[0].data
        s_envb3 = obspy.signal.filter.envelope(stb3[0].data) # Highlights slower changes in amplitude; a smooth curve that follows the local maxima
        s_env_smoothb3 = smooth(s_envb3, samples)

############################### B4
        #Empty trace check
        if len(stb4) ==0:
            print('empty trace')
            continue
        trb4 = stb4[0]  

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

        
        try:
            stb4.merge(fill_value='interpolate')  # Merge traces, filling gaps with interpolation
            print(f'Merged traces for {stz[j]} on {th_day[i]} successfully.')
        except Exception as e:
            print(f'Error merging traces for {stz[j]} on {th_day[i]}: {e}')


        sb4=stb4[0].data
        sb4graph=stb4[0].data
        stb4.detrend("demean")
        stb4.detrend("linear")
        stb4.filter('bandpass',freqmin=fminb4,freqmax=fmaxb4) 
        tr_b4=stb4[0]
        s_envb4=stb4[0].data
        s_filtb4 = stb4[0].data
        s_envb4 = obspy.signal.filter.envelope(stb4[0].data)
        s_env_smoothb4 = smooth(s_envb4, samples) # 3000 so 60 sec

### def window 10 sec
        sampling_rate = trb3.stats.sampling_rate  

# 1 day
        start_time = UTCDateTime(trb3.stats.starttime.date)  # 00:00:00 du jour actuel
        end_time = start_time + 86400  # 86400 secondes = 24 heures

# create list for storage results
        results = []

        current_time = start_time 
        while current_time < end_time:
    # window : 5 sec before and 5 sec after (12:40:10 => 12:40:05 & 12:40:15)
            window_start = current_time - 5  # 5 sec before
            window_end = current_time + 5  # 5 sec after
    
    # index window 10 sec
            start_index = int((window_start - tr_b3.stats.starttime) * sampling_rate)
            end_index = int((window_end - tr_b3.stats.starttime) * sampling_rate)
############################### B3
            if 0 <= start_index < len(tr_b3.data) and 0 <= end_index <= len(tr_b3.data):
                window_datab3 = s_env_smoothb3[start_index:end_index]
        
        # 10 seconds for each window
                if len(window_datab3) == 10 * sampling_rate:
                    mean_valueb3 = np.mean(window_datab3)  # mean
                else:
                    mean_valueb3 = np.nan  # incomplete => NaN
            else:
                mean_valueb3 = np.nan  # missing data or no valide index 
############################### B4
   
            if 0 <= start_index < len(tr_b4.data) and 0 <= end_index <= len(tr_b4.data):
                window_datab4 = s_env_smoothb4[start_index:end_index]
        
                if len(window_datab4) == 10 * sampling_rate:
                    mean_valueb4 = np.mean(window_datab4)  
                else:
                    mean_valueb4 = np.nan 
            else:
                mean_valueb4 = np.nan 


    # add in list
            results.append((current_time, mean_valueb3, mean_valueb4))

    # next 10 sec
            current_time += 10  

        times = [entry[0].datetime for entry in results]  # convert UTCDateTime en datetime
        meansb3 = [entry[1] for entry in results]  # extract mean
        meansb4 = [entry[2] for entry in results]

            ### CREATING MY CSV FILE
        df = pd.DataFrame()

        df['time_UTC'] = times
        df['RSAM_env_smooth_1-8Hz'] = meansb3
        df['RSAM_env_smooth_8-15Hz'] = meansb4

        csv_filename = os.path.join(save_dir, f'rsam_{stz[j]}_{th_day[i].strftime("%Y%m%d")}.csv')
        df.to_csv(csv_filename, index=False)
        print(f'My file name is ', csv_filename)