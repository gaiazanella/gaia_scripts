### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/'
stz = ['STR*']
net = ['I*']
channel = ['*HZ']
#channel = ['*H*']


# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-01-23T19:30:00.000")
#tf = ti + (60 * 60 * 1) # 1 heure de données
tf= ti+ (60*60)  

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
#stvlp = client.get_waveforms(network=net[0], station='STR1', location="", channel=channel[0], starttime=ti, endtime=tf)
#stvlp.integrate().filter('bandpass',freqmin=1/30,freqmax=1)
#st1+=stvlp

#st1.write('/home/gaia/Documents/mseed_terremoti/qf_terremoti/20240801_5_1.mseed')
#st1.write('/home/gaia/Documents/mseed_terremoti/qf_terremoti/20240801_5_1_compoz.mseed')
#st1.write('/home/gaia/Documents/lds_gt_4000/20201116_09_18.mseed')
st1.plot()
