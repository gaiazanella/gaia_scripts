import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.interpolate import interp1d
from obspy import read
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy import interpolate
from obspy import read
from scipy.signal import detrend
from obspy.signal.util import smooth

stream_station = read("/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed")
stream_station.detrend("demean") #met le signal autour de zéro 
stream_station.detrend("linear") 

tt = stream_station[0].times()

trace_station_stra = stream_station[8]
print(trace_station_stra)
trace_station_stre = stream_station[14]
print(trace_station_stre)
trace_station_strc = stream_station[11]
print(trace_station_strc)
trace_station_strg = stream_station[17]
print(trace_station_strg)
trace_station_str1 = stream_station[2]
print(trace_station_str1)
trace_station_str4 = stream_station[5]
print(trace_station_str4)

data_station_stra = trace_station_stra.data
data_station_stre = trace_station_stre.data
data_station_strc = trace_station_strc.data
data_station_strg = trace_station_strg.data
data_station_str1 = trace_station_str1.data
data_station_str4 = trace_station_str4.data

#data_station_stra=data_station_stra*3.18**(-6)/800 ## STRA
#data_station_strc=data_station_strc*3.18**(-6)/800 ## STRC
#data_station_stre=data_station_stre*3.18**(-6)/800 ## STRE
#data_station_strg=data_station_strg*3.18**(-6)/800 ## STRG
#data_station_str1=data_station_str4*3.18**(-6)/800 ## STR4
#data_station_str4=data_station_str1*3.18**(-6)/800 ## STR1
 
# Plot des différentes données
fig, axs = plt.subplots(6, 1, figsize=(10, 12))  # 6 graphiques verticaux
axs[0].plot(tt, data_station_stra, color='r', label='Station A')
axs[1].plot(tt, data_station_stre, color='b',  label='Station E')
axs[2].plot(tt, data_station_strc, color='g',  label='Station C')
axs[3].plot(tt, data_station_strg, color='m', label='Station G')
axs[4].plot(tt, data_station_str1, color='c', label='Station 1')
axs[5].plot(tt, data_station_str4, color='y', label='Station 4')
for i, ax in enumerate(axs):
    #ax.set_ylabel('Seismic record\n(m/s)') # Nomme chaque station sur l'axe y
    ax.set_ylabel('Seismic record\n(count)') # Nomme chaque station sur l'axe y
    ax.legend(loc='best')
    ax.grid(True)
axs[5].set_xlabel('Time (s)')
plt.subplots_adjust(hspace=0.5)
plt.show()

fff

def smoothlog(data, window_length):
    log_data = np.log(data)  
    smoothed = np.convolve(log_data, np.ones(window_length) / window_length, mode='same')
    return np.exp(smoothed)  

stream_station = read("/home/gaia/Documents/mseed_terremoti/20201021_M5.2.mseed")
print(stream_station[1])

stream_station.detrend("demean")
stream_station.detrend("linear")

print(stream_station)


n = 6  
m = 18001 

data = np.zeros((m, n))

tt = stream_station[0].times()

data[:,0] = stream_station[2]
data[:,1] = stream_station[5]
data[:,2] = stream_station[8]
data[:,3] = stream_station[11]
data[:,4] = stream_station[14]
data[:,5] = stream_station[17]
print(len(tt))
print(len(data))

STZ = ['STR1','STR4','STRA', 'STRC', 'STRE', 'STRG']
sconv = [(3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800)]  # Facteurs de conversion (ajuster selon les données)
tt = stream_station[0].times()
############
plt.figure()
plt.plot(tt, data)
#plt.plot(tt, data[:,:,2])  # Composante 0 de 'data'
plt.pause(0.1)

a = plt.ginput(2)  #seleziono dalla traccia un intervallo temporale su cui voglio fare l'analisi
a = np.sort(a, axis=0)

PXX = []

for i in range(len(STZ)):  # ciclo per ogni stazione
    yy = data[:,i]
    #yy = data[:,i,2] # seleizono la traccia associata alla stazione, componente 3 (la verticale). 
                    #data: la matrice di dati convertiti in m/s di dimensione mxnx3 
                    # dove m=numero di dati, n:numero di stazioni, 3: le componenti

    
    ii = np.where((tt > a[0, 0]) & (tt < a[1, 0]))[0]
    tt_selected = tt[ii]
    yy_selected = yy[ii] * sconv[i] 
    
    #smp = (tt_selected[1] - tt_selected[0]) * 86400
    smp = (tt_selected[1] - tt_selected[0])
    print(smp)
    smp = round(1. / smp)
    print(smp)  # calcolo il sample rate passo di giorni a secondi

    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16) #faccio lo spettro di ampiezza
    
    PXX.append(pxx)

PXX = np.array(PXX)

# mi salvo gli indici del ritaglio temporale selezionato
isel = ii

iref = 3  #definisco la stazione di riferimento (la 6 in questo caso)

ii_f = np.where((f > 0.01) & (f < 24))[0] #definisco l'intervallo di frequenza da analizzare
a0 = smooth(PXX[iref, ii_f], 100)  # salvo dentro a0 lo spettro di riferimento, opportunamento smoothato

A = []
Am = []
ratio = []

for i in range(len(STZ)):  # nuovo ciclo per tutte le stazioni
    ratio_i = np.sqrt(smooth(PXX[i, ii_f],100) / a0)
    
    A.append(np.mean(ratio_i))  #media del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    Am.append(np.std(ratio_i))  #%dev.std del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    ratio.append(ratio_i)  #rapporti spettrali originali salvati dentro ratio

A = np.array(A)
Am = np.array(Am)
ratio = np.array(ratio)

########################
# RP each station
plt.figure(figsize=(10, 6))
for i, ratio_i in enumerate(ratio):
    plt.plot(f[ii_f], ratio_i, label=f"Station {STZ[i]}")  # f[ii_f] : fréquence dans la plage sélectionnée
plt.xlabel('Frequency (Hz)')
plt.ylabel('Spectral Ratio')
plt.xscale('log')
plt.legend()
plt.title('Spectral Ratios for each Station relative to Reference')
plt.grid(True)
plt.show()

#########################
# AM each station
plt.figure(figsize=(10, 6))
plt.bar(STZ, A, yerr=Am, capsize=5, color='skyblue', edgecolor='black')
plt.xlabel('Station')
plt.ylabel('Mean Spectral Ratio')
plt.title('Mean Spectral Ratios for each Station')
plt.grid(True)
plt.show()

#############################
# ppx each station
plt.figure(figsize=(12, 8))
for i in range(len(STZ)): 
    yy = data[:, i]  
    
    ii = np.where((tt > a[0, 0]) & (tt < a[1, 0]))[0] 
    tt_selected = tt[ii]
    yy_selected = yy[ii] * sconv[i]  
    
    smp = (tt_selected[1] - tt_selected[0])  
    smp = round(1. / smp)  
    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16)  
    
    plt.plot(f, smooth(pxx,100), label=f"Station {STZ[i]}")  

plt.xlabel('Frequency (Hz)')
plt.xscale('log')
plt.ylabel('Power Spectral Density (Amplitude^2/Hz)')
plt.legend()
plt.title('Power Spectrum of each Station')
plt.grid(True)
plt.show()


#############################
plt.figure(figsize=(12, 8))  

nrows = 2  
ncols = 3  

for i in range(len(STZ)): 
    yy = data[:, i]  
    
    ii = np.where((tt > a[0, 0]) & (tt < a[1, 0]))[0]  
    tt_selected = tt[ii]
    yy_selected = yy[ii] * sconv[i] 

    smp = (tt_selected[1] - tt_selected[0])  
    smp = round(1. / smp)  
    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16)  
    
    plt.subplot(nrows, ncols, i + 1)  
    plt.plot(f, smooth(pxx,100))
    plt.xlabel('Frequency (Hz)')
    plt.xscale('log')
    plt.ylabel('Power Spectral Density (Amplitude^2/Hz)')
    plt.title(f"Station {STZ[i]}")
    plt.grid(True)

plt.suptitle('Power Spectrum of Each Station', fontsize=16)

plt.tight_layout()
plt.subplots_adjust(top=0.88) 
plt.show()

