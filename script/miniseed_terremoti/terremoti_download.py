### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

# Paramètres
db = '/mnt/bigmama3/miniseed'
stz = ['STR*']
net = ['I*']
channel = ['*H*']

# Client pour récupérer les données
client = Client(db)
ti = UTCDateTime("2020-03-21T00:49:00.000")
tf = ti + (60 * 13 * 1)  # 6 min de données

# Récupérer les données pour les deux stations
st1 = client.get_waveforms(network=net[0], station=stz[0], location="", channel=channel[0], starttime=ti, endtime=tf)
st1.write('/home/gaia/Documents/mseed_terremoti/20200321_M5.7.mseed')
st1.plot()
