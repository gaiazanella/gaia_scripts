### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3'
stz = ['STR*']
net = ['I*']
channel = ['*HZ']
#channel = ['*H*']


# Client pour récupérer les données
client = Client(db)
#ti = UTCDateTime("2022-12-04T15:17:00.000")
#tf = ti + (60 * 60 * 1) # 1 heure de données

times = [
    UTCDateTime("2019-07-03T14:44:00"),
    UTCDateTime("2019-08-28T10:16:00"),
    UTCDateTime("2020-11-16T09:15:30"), #fait avant 09:17:00 # apres 10 min
    UTCDateTime("2021-05-19T12:50:00"), 
    UTCDateTime("2022-10-09T07:21:40"),
    UTCDateTime("2022-12-04T15:17:00"),
    UTCDateTime("2020-04-15T07:13:00"), #fait avant 07:21:00 # apres 40 min
    UTCDateTime("2020-07-19T02:57:00"), #fait avant 02:59:00 # apres 22 min
    UTCDateTime("2020-11-10T20:00:00"), #fait avant 20:03:00 # apres 19 min
    UTCDateTime("2020-03-31T01:40:00"),

]
ti=times[4]
tf= ti+ (60*22) #bf 4
#ti=UTCDateTime("2020-01-10T12:00:00")
#tf= ti + 60*60

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
print(st1)

#fff
#stvlp = client.get_waveforms(network=net[0], station='STR1', location="", channel=channel[0], starttime=ti, endtime=tf)
#stvlp.integrate().filter('bandpass',freqmin=1/30,freqmax=1)
#st1+=stvlp

#st1.write('/home/gaia/Documents/mseed_terremoti/qf_terremoti/20240801_5_1.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev_piu_lungo/20201116_compoz.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev/20201110_compoz.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev/20200415_compoz_STRA.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev/20200415_compoz_STRE.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev/20200415_compoz_STRG.mseed')
#st1.write('/home/dario/Documenti/20221204.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev_piu_lungo/20200415_compoz.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev_piu_lungo/20200719_compoz.mseed')
#st1.write('/home/dario/Documenti/volume/miniseed_big_ev_piu_lungo/20201110_compoz.mseed')
st1.plot()
