from obspy import Stream
## PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')  # ou 'TkAgg' selon ton système
import matplotlib.pyplot as plt

# Paramètres
db = '/mnt/bigmama3'
net = ['I*']
channel = ['*HZ']
#ti = UTCDateTime("2022-10-09T07:00:40")
#ti = UTCDateTime("2022-12-04T15:00:00")
ti = UTCDateTime("2019-07-03T14:00:00")
#tf = ti + (60 * 60 * 1) # 1 heure de données
tf= ti+ (60*60)*1
#channel = ['*H*']

#t1 = UTCDateTime("2022-10-09T07:23:10")
#t2 = UTCDateTime("2022-10-09T07:23:30")
#t1 = UTCDateTime("2022-10-09T07:23:08") #ti FB
#t2 = UTCDateTime("2022-10-09T07:23:30") #tf FB
#t1 = UTCDateTime("2022-12-04T15:18:12") #ti FB
#t2 = UTCDateTime("2022-12-04T15:18:24") #tf FB
#t1 = UTCDateTime("2022-12-04T15:18:10")
#t2 = UTCDateTime("2022-12-04T15:18:20")

# Client pour récupérer les données
client = Client(db)
stations = ['STRA', 'STRE', 'STRG', 'STRC']
st1 = Stream()

for sta in stations:
    st = client.get_waveforms(
        network=net[0],
        station=sta,
        location="",
        channel=channel[0],
        starttime=ti,
        endtime=tf
    )
    st1 += st

print(st1)
st1.plot()

