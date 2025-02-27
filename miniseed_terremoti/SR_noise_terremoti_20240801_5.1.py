import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from obspy import read
from obspy.signal.util import smooth
from scipy.signal import welch, detrend
import numpy as np
import matplotlib.pyplot as plt
from obspy import read

# Lire les données
stream_station = read("/home/gaia/Documents/mseed_terremoti/miniseed_terremoti_selected/z_composant/20240801_M5.1.mseed")
print(stream_station)
stream_station.detrend("demean")
stream_station.detrend("linear")
sconv1=1*10**(-6)
sconv2=1200
sconv=sconv1/sconv2
print(sconv)
stream_station.plot()

#n = 6  # Nombre de stations
n=5
m = 60001  # Nombre d'échantillons

data = np.zeros((m, n))
x=189*(3.18*10**(-6))/800
print(x)

# Récupérer les données pour chaque station
data[:, 0] = stream_station[2].data  # STR6
print(stream_station[2])
data[:, 4] = stream_station[3].data  # STRA
print(stream_station[3])
data[:, 1] = stream_station[4].data  # STRC
print(stream_station[4])
data[:, 2] = stream_station[5].data  # STRE
print(stream_station[5])
data[:, 3] = stream_station[6].data  # STRG
print(stream_station[6])
#print(data)

# Créer un tableau avec les noms des stations
STZ = ['STR6', 'STRA', 'STRC', 'STRE', 'STRG']
#STZ = ['STRA']

# Tracer toutes les stations sur le même graphique
plt.figure(figsize=(10, 6))

# Tracer chaque station
for i in range(n):
    print(f"Contenu de data[:, {i}] :")
    print(data[:, i])
    print(f"Contenu de data[:, {i}] après multiplication par sconv :")
    print(data[:, i]*sconv)
    plt.plot(stream_station[2].times(), (data[:, i]*sconv), label=STZ[i])

# Ajouter des labels et un titre
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude")
#plt.ylim(-1.5**(-5), 2.5**(-5))
plt.title("Traces des stations")
plt.legend()
plt.show()

tt = stream_station[2].times()


# Définir les intervalles de temps que vous voulez analyser (0-50s et 150-200s)
interval_1 = (0, 100)
interval_2 = (180, 280)

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
    yy_selected_1 = yy[ii_1] * sconv 
    #yy_selected_1_detrended = detrend(yy_selected_1)

    smp_1 = (tt_selected_1[1] - tt_selected_1[0]) 
    smp_1 = round(1. / smp_1)  
    #f_1, pxx_1 = welch(yy_selected_1, fs=smp_1, nperseg=2**16)  
    nperseg_1=min(2**16, len(yy_selected_1))
    f_1, pxx_1 = welch(yy_selected_1, fs=smp_1, nperseg=nperseg_1) 
    PXX_1.append(pxx_1)
    
    # Intervalle 2 (150-200s)
    tt_selected_2 = tt[ii_2]
    yy_selected_2 = yy[ii_2] * sconv  
    
    smp_2 = (tt_selected_2[1] - tt_selected_2[0])  
    smp_2 = round(1. / smp_2) 
    #yy_selected_2_detrended = detrend(yy_selected_2)
    nperseg_2=min(2**16, len(yy_selected_1))
    f_2, pxx_2 = welch(yy_selected_2, fs=smp_2, nperseg=nperseg_2) 
    #f_2, pxx_2 = welch(yy_selected_2, fs=smp_2, nperseg=2**16)  
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
plt.yscale('log')
plt.xlabel('Frequency (Hz)')
#plt.ylabel('Power Spectral Density (Amplitude^2/Hz)')
plt.ylabel(r'PSD $(\text{m/s})^2/\text{ Hz}$')
plt.legend()
#plt.title('Power Spectrum for Different Time Intervals')
plt.grid(True, which="both", ls="--")  # Afficher la grille pour les axes log
plt.show()

##STRC
iref = 2
#ii_f = np.where((f_1 > 0.01) & (f_1 < 24))[0] #definisco l'intervallo di frequenza da analizzare
ii_f = np.where((f_1 > 8) & (f_1 < 15))[0] #definisco l'intervallo di frequenza da analizzare
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