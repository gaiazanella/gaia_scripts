import obspy
from obspy.clients.fdsn import Client
from obspy.imaging.spectrogram import spectrogram
client = Client("IRIS")
from obspy import UTCDateTime
import numpy as np
import matplotlib.pyplot as plt



# Retrieve waveform data
t1 = UTCDateTime("2020-02-13T09:02:00.000")
t2 = UTCDateTime("2020-02-13T09:28:00.000")

# get_waveforms expects (network, station, location, channel, start_time, end_time)
# One station/channel
st = client.get_waveforms("IM","H11S1","","EDH",t1,t2)

""" Plot the timeseries waveform """
st.plot()


""" Plot the spectrogram """
fig = st.spectrogram(log=False, dbscale=True, axes=None, title='Spectrogram', cmap='inferno', show=False)
fig.axes[0].set_ylim(0,100)
plt.show()