from obspy.clients.filesystem.sds import Client
from obspy import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend  # Correct import of detrend
import numpy as np
from obspy.signal.util import smooth 

st=read('/home/gaia/Documents/mseed_terremoti/miniseed_terremoti_selected/z_composant/20250207.mseed')
st.plot()
print(st)

Pxx = {}
f = None

plt.figure(figsize=(8, 5))
Pxx_all_stations = {}
f_all_stations = None

stations = ['STRA', 'STRC', 'STRE', 'STRG']

for i in stations:
            ss=st.select(station=i)
            data = ss[0].data
            data = detrend(data) 

            fs = 100
            nperseg = len(data)
            noverlap = 128

            f, Pxx = welch(data * 1E-6 / 1200, fs=fs, nperseg=2**16)
            Pxx_all_stations[i] = Pxx
    
            plt.loglog(f, Pxx, label=f"{i}", linestyle='-', alpha=0.7) 

plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()
print(Pxx_all_stations['STRA'])
print(len(f))

plt.figure(figsize=(8, 5))
Pxx_ref= Pxx_all_stations['STRA']
ii_f = np.where((f > 8) & (f < 15))[0]
print(ii_f)

ratio_mean=[]

for i in stations:
        ratio=np.sqrt(Pxx_all_stations[i]/Pxx_ref)
        ratio_mean=np.mean(ratio[ii_f])
        print(ratio_mean)
        plt.semilogx(f, smooth(ratio,100), label=f"{i}", linestyle='-', alpha=0.7)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Ratio")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()