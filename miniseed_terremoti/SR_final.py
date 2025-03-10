from obspy.clients.filesystem.sds import Client
#from obspy.clients.fdsn import Client as Eida
from numpy import arange
#from obspy.clients.seedlink import Client
from obspy import UTCDateTime
import matplotlib.pyplot as plt
from scipy.signal import welch
import numpy as np

from obspy.signal.util import smooth
#import numpy as np
#from pyrocko import pile
###import matplotlib.pyplot as plt
##client = Client("/mnt/bigmama3")
#client = Client("/home/dario/Documenti/CPIS.EDF")
client = Client("/mnt/bigmama3")

##d
##dd
#t = UTCDateTime("2024-01-23T23:00:00")
##t = UTCDateTime("2022-11-09T06:07:00")
#t = UTCDateTime("2022-11-26T02:14:00")
##t = UTCDateTime("2024-08-22")
#t = UTCDateTime("2025-02-07T15:18:30")
t = UTCDateTime("2025-02-07T15:19:30")
#dt=1*3600 ### 
dt = 30
##dt=60*10
##dt=5*60
##tsel=["2023-03-14T16:36:03","2023-01-23T10:37:53","2022-10-31T21:42:50","2022-10-08T22:02:28","2022-09-08T07:36:24"]
##t=UTCDateTime(tsel[4])
##t=UTCDateTime.now()-86400
##dt=86400
print(t)
##stz=['*']
##ch=['*DF']
stz = ['STR*']
ch=['*HZ']
##ch=['HHZ','EHZ','HHZ','EHZ','EHZ','HHZ','HHZ','HHZ']
sz = client.get_waveforms(network="*",station=stz[0],location= "*", channel= ch[0], starttime =t,endtime=t+dt)
sz.plot()
print((sz))

##sz += client.get_waveforms(network="*",station='CPIS',location= "*", channel= 'HHZ', starttime =t,endtime=t+dt)
data=sz[0].data
fs=100
nperseg=len(data)
noverlap=128
 # Compute the spectrogram using Welch's metho
f, Pxx = welch(data*1E-6/800, fs=fs, nperseg=nperseg)   # Convert power spectral density to dB
##Sxx_dB = 10 * np.log10(Sxx + 1e-12)  # Avoid log(0)
plt.figure(figsize=(8, 5))
plt.loglog(f, smooth(Pxx,100), label="Amplitude Spectrum (Welch)", color='b')
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Amplitude Spectrum using Welch's Method")
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.show()
dd
##sz.filter('bandpass',freqmin=8,freqmax=40)
sz.plot(equal_scale=False,method='Full')
print(sz[0].stats.starttime)
