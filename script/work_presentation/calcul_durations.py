### PACKAGES
from obspy import UTCDateTime
from obspy.signal.filter import bandpass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy.clients.filesystem.sds import Client

ti=UTCDateTime("2020-03-31T01:46:36.500")
tf = UTCDateTime("2020-03-31T01:47:02.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T02:34:45.500")
tf = UTCDateTime("2020-03-31T02:35:27.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T02:38:50.000")
tf = UTCDateTime("2020-03-31T02:42:32.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T02:40:00.000")
tf = UTCDateTime("2020-03-31T02:45:07.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T02:50:54.500")
tf = UTCDateTime("2020-03-31T02:51:42.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T02:55:13.000")
tf = UTCDateTime("2020-03-31T02:56:03.500")

print(tf-ti)

ti=UTCDateTime("2020-03-31T03:00:19.000")
tf = UTCDateTime("2020-03-31T03:01:04.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T03:05:43.000")
tf = UTCDateTime("2020-03-31T03:06:23.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T03:30:00.000")
tf = UTCDateTime("2020-03-31T03:31:27.000")

print(tf-ti)

ti=UTCDateTime("2020-03-31T03:41:17.000")
tf = UTCDateTime("2020-03-31T03:41:57.000")

print(tf-ti)