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
sconv = [(3.18**(-6)/800), (3.28**(-6)/800), (3.18**(-6)/800), (1.00**(-6)/1200), (3.20**(-6)/800), (1.00**(-6)/1200)]  # Facteurs de conversion (ajuster selon les données)
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
    yy_selected = yy[ii] / sconv[i] 
    
    #smp = (tt_selected[1] - tt_selected[0]) * 86400
    smp = (tt_selected[1] - tt_selected[0])
    smp = round(1. / smp)  # calcolo il sample rate passo di giorni a secondi

    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16) #faccio lo spettro di ampiezza
    
    PXX.append(pxx)

PXX = np.array(PXX)

# mi salvo gli indici del ritaglio temporale selezionato
isel = ii

iref = 5  #definisco la stazione di riferimento (la 6 in questo caso)

ii_f = np.where((f > 7) & (f < 15))[0] #definisco l'intervallo di frequenza da analizzare
a0 = smoothlog(PXX[iref, ii_f], 1)  # salvo dentro a0 lo spettro di riferimento, opportunamento smoothato

A = []
Am = []
ratio = []

for i in range(len(STZ)):  # nuovo ciclo per tutte le stazioni
    ratio_i = np.sqrt(smoothlog(PXX[i, ii_f] / a0, 1))
    
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
    yy_selected = yy[ii] / sconv[i]  
    
    smp = (tt_selected[1] - tt_selected[0])  
    smp = round(1. / smp)  
    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16)  
    
    plt.plot(f, pxx, label=f"Station {STZ[i]}")  

plt.xlabel('Frequency (Hz)')
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
    yy_selected = yy[ii] / sconv[i] 

    smp = (tt_selected[1] - tt_selected[0])  
    smp = round(1. / smp)  
    f, pxx = welch(yy_selected, fs=smp, nperseg=2**16)  
    
    plt.subplot(nrows, ncols, i + 1)  
    plt.plot(f, pxx) 
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (Amplitude^2/Hz)')
    plt.title(f"Station {STZ[i]}")
    plt.grid(True)

plt.suptitle('Power Spectrum of Each Station', fontsize=16)

plt.tight_layout()
plt.subplots_adjust(top=0.88) 
plt.show()

