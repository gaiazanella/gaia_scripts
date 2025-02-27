import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from obspy import read
from obspy.signal.util import smooth

stream_station = read("/home/gaia/Documents/mseed_terremoti/20240801_M5.1.mseed")
stream_station.detrend("demean")
stream_station.detrend("linear")
print(len(stream_station))

#stream_station.plot()

for i in range(24):
    print(f'trace_station_str6 = {stream_station[i]}')
    print (i)

tt = stream_station[9].times()

#trace_station_str1 = stream_station[0]
#print(trace_station_str1)

trace_station_str6 = stream_station[9]
print(trace_station_str6)
trace_station_stra = stream_station[12]
print(trace_station_stra)
trace_station_strc = stream_station[16]
print(trace_station_strc)
trace_station_stre = stream_station[20]
print(trace_station_stre)
trace_station_strg = stream_station[24]
print(trace_station_strg)
#trace_station_str1 = stream_station[2]
#print(trace_station_str1)

data_station_stra = trace_station_stra.data
data_station_stre = trace_station_stre.data
data_station_strc = trace_station_strc.data
data_station_strg = trace_station_strg.data
#data_station_str1 = trace_station_str1.data
data_station_str6 = trace_station_str6.data

data_station_stra=data_station_stra*3.18**(-6)/800 ## STRA
data_station_strc=data_station_strc*3.18**(-6)/800 ## STRC
data_station_stre=data_station_stre*3.18**(-6)/800 ## STRE
data_station_strg=data_station_strg*3.18**(-6)/800 ## STRG
#data_station_str1=data_station_str1*3.18**(-6)/800 ## STR4
data_station_str6=data_station_str6*3.18**(-6)/800 ## STR6
 
# Plot des différentes données
fig, axs = plt.subplots(5, 1, figsize=(10, 12))  # 6 graphiques verticaux
axs[0].plot(tt, data_station_stra, color='r', label='STRA')
axs[1].plot(tt, data_station_stre, color='b',  label='STRE')
axs[2].plot(tt, data_station_strc, color='g',  label='STRC')
axs[3].plot(tt, data_station_strg, color='m', label='STRG')
#axs[4].plot(tt, data_station_str1, color='c', label='Station 1')
axs[4].plot(tt, data_station_str6, color='y', label='STR6')
for i, ax in enumerate(axs):
    ax.set_ylabel('Seismic record\n(m/s)') # Nomme chaque station sur l'axe y
    #ax.set_ylabel('Seismic record\n(count)') # Nomme chaque station sur l'axe y
    ax.legend(loc='best')
    ax.grid(True)
axs[4].set_xlabel('Time (s)')
plt.subplots_adjust(hspace=0.5)
plt.show()

n = 5  
m = len(stream_station[9].data)

data = np.zeros((m, n))

data[:,0] = stream_station[9]
data[:,1] = stream_station[12]
data[:,2] = stream_station[16]
data[:,3] = stream_station[20]
data[:,4] = stream_station[24]

STZ = ['STR6','STRA', 'STRC', 'STRE', 'STRG']
sconv = [(3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800), (3.18**(-6)/800)]  

# Définir les intervalles de temps que vous voulez analyser (0-50s et 150-200s)
interval_1 = (50, 100)
interval_2 = (170, 220)

# Convertir les intervalles de temps en indices
ii_1 = np.where((tt > interval_1[0]) & (tt < interval_1[1]))[0]
ii_2 = np.where((tt > interval_2[0]) & (tt < interval_2[1]))[0]

# Calculer le PSD pour les deux intervalles
PXX_1 = []
PXX_2 = []

for i in range(len(STZ)):  
    yy = data[:, i]  
    
    # Intervalle 1 (0-50s)
    tt_selected_1 = tt[ii_1]
    yy_selected_1 = yy[ii_1] * sconv[i]  
    
    smp_1 = (tt_selected_1[1] - tt_selected_1[0])  
    smp_1 = round(1. / smp_1)  
    f_1, pxx_1 = welch(yy_selected_1, fs=smp_1, nperseg=2**16)  
    PXX_1.append(pxx_1)
    
    # Intervalle 2 (150-200s)
    tt_selected_2 = tt[ii_2]
    yy_selected_2 = yy[ii_2] * sconv[i]  
    
    smp_2 = (tt_selected_2[1] - tt_selected_2[0])  
    smp_2 = round(1. / smp_2)  
    f_2, pxx_2 = welch(yy_selected_2, fs=smp_2, nperseg=2**16)  
    PXX_2.append(pxx_2)

PXX_1 = np.array(PXX_1)
PXX_2 = np.array(PXX_2)

# Afficher les résultats sur le même graphique avec l'axe des x en log
plt.figure(figsize=(12, 8))

for i in range(len(STZ)): 
    # PSD pour l'intervalle 0-50s
    plt.plot(f_1, smooth(PXX_1[i], 100), label=f"Station {STZ[i]} noise")  
    
    # PSD pour l'intervalle 150-200s
    plt.plot(f_2, smooth(PXX_2[i], 100), label=f"Station {STZ[i]} event", linestyle='--')  

# Changer l'échelle de l'axe des x en logarithmique
plt.xscale('log')
plt.xlabel('Frequency (Hz)')
#plt.ylabel('Power Spectral Density (Amplitude^2/Hz)')
plt.ylabel(r'PSD $(\text{m/s})^2/\text{ Hz}$')
plt.legend()
#plt.title('Power Spectrum for Different Time Intervals')
plt.grid(True, which="both", ls="--")  # Afficher la grille pour les axes log
plt.show()

iref = 2
ii_f = np.where((f_1 > 0.01) & (f_1 < 24))[0] #definisco l'intervallo di frequenza da analizzare
#ii_f = np.where((f_1 > 8) & (f_1 < 15))[0] #definisco l'intervallo di frequenza da analizzare
a0_1 = smooth(PXX_1[iref, ii_f], 100)  # salvo dentro a0 lo spettro di riferimento, opportunamento smoothato
a0_2 = smooth(PXX_2[iref, ii_f], 100)  # salvo dentro a0 lo spettro di riferimento, opportunamento smoothato

A_1 = []
Am_1 = []
ratio_1 = []

for i in range(len(STZ)):  # nuovo ciclo per tutte le stazioni
    ratio_i = np.sqrt(smooth(PXX_1[i, ii_f],100) / a0_1)
    
    A_1.append(np.mean(ratio_i))  #media del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    Am_1.append(np.std(ratio_i))  #dev.std del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    ratio_1.append(ratio_i)  #rapporti spettrali originali salvati dentro ratio

A_1 = np.array(A_1)
Am_1 = np.array(Am_1)
ratio_1 = np.array(ratio_1)

A_2 = []
Am_2 = []
ratio_2 = []
for i in range(len(STZ)):  # nuovo ciclo per tutte le stazioni
    ratio_i = np.sqrt(smooth(PXX_2[i, ii_f],100) / a0_1)
    
    A_2.append(np.mean(ratio_i))  #media del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    Am_2.append(np.std(ratio_i))  #%dev.std del rapporto spettrale tra lo spettro i-esimo e quello di riferimento
    ratio_2.append(ratio_i)  #rapporti spettrali originali salvati dentro ratio

A_2 = np.array(A_2)
Am_2 = np.array(Am_2)
ratio_2 = np.array(ratio_2)

# SR each station
plt.figure(figsize=(10, 6))
for i, ratio_i in enumerate(ratio_1):
    plt.plot(f_1[ii_f], ratio_i, label=f"Station {STZ[i]} noise")  # f[ii_f] : fréquence dans la plage sélectionnée
for i, ratio_i in enumerate(ratio_2):
    plt.plot(f_2[ii_f], ratio_i, label=f"Station {STZ[i]} event", linestyle='--')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Spectral Ratio')
plt.xscale('log')
plt.legend()
#plt.title('Spectral Ratios for each Station relative to Reference')
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
plt.bar(STZ, A_2, yerr=Am_2, capsize=5, color=(1, 0.5, 0, 0.5), edgecolor='black', label='Event')  # Orange transparent
plt.bar(STZ, A_1, yerr=Am_1, capsize=5, color=(0.1, 0.6, 1, 0.5), edgecolor='black', label='Noise')  # Bleu transparent
plt.xlabel('Station')
plt.ylabel('Mean Spectral Ratio')
plt.legend()
#plt.title('Mean Spectral Ratios for each Station')
plt.grid(True)
plt.show()

print(A_1)
print(A_2)
print(Am_1)
print(Am_2)