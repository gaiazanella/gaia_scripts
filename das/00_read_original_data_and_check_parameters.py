# import librairies
import numpy as np
import sys
import os
import glob
import re

import h5py


def print_h5_structure(f, level=0):
    """    prints structure of hdf5 file    """
    for key in f.keys():
        if isinstance(f[key], h5py._hl.dataset.Dataset):
            print(f"{'  '*level} DATASET: {f[key].name}")
        elif isinstance(f[key], h5py._hl.group.Group):
            print(f"{'  '*level} GROUP: {key, f[key].name}")
            level += 1
            print_h5_structure(f[key], level)
            level -= 1

        if f[key].parent.name == "/":
            print("\n"*2)


# Define relevant variables
 ########## EDIT HERE #############################################################
#
#DAS_PROJ="DAS_INGV_08"            #   DAS_BIC_03  or DAS_BIC_16 or DAS_INGV_02
#DATA_REPO="/Users/nicola/DAS-INGV-08-repo/"
DATA_REPO="/home/dario/Documenti/das_nicola/mission_2026_giu/"
target_datafile = 'DAS_INGV_08_2026-06-30_19-00-54_UTC.h5'
#
########## EDIT HERE #############################################################


h5_file = DATA_REPO + target_datafile

print('Working on file: ', h5_file)

#Read HDF5 file

with h5py.File(h5_file, "r") as f:
    # List all groups
    print("DAS interrogator S/N: %s" % f.keys())
    a_group_key = list(f.keys())[0]

    # Get the data
    data = list(f[a_group_key])

# Information on the experimental set-up
f = h5py.File(h5_file, 'r')

print("\nSTRUCTURE:")
print_h5_structure(f)

print("Fiber Length, in meters: %s" % f['/fa1-24090172/Source1'].attrs['FiberLength'])
print("PRF: (x1000)%s" % f['/fa1-24090172/Source1'].attrs['PulseRateFreq'])
print("BLOCK RATE , in ms: %s" % f['/fa1-24090172/Source1'].attrs['BlockRate'])
print("BLOCK OVERLAP, in percent: %s" % f['/fa1-24090172/Source1'].attrs['BlockOverlap'])
print("PULSE WIDTH: in m %s" % f['/fa1-24090172/Source1'].attrs['PulseWidth'])
print("AMPLI POWER: in dB %s" % f['/fa1-24090172/Source1'].attrs['AmpliPower'])
print("SAMPLING RESOLUTION: in cm %s" % f['/fa1-24090172/Source1'].attrs['SamplingRes'])

print("\nGAUGE LENGTH: in meters %s" % f['/fa1-24090172/Source1/Zone1'].attrs['GaugeLength'])
print("CHANNEL SPACING, in meters: %s" % f['/fa1-24090172/Source1/Zone1'].attrs['Spacing'][0])
print("DELTA TIME, in ms: %s" % f['/fa1-24090172/Source1/Zone1'].attrs['Spacing'][1])
print("Number of Channels: %s" % f['/fa1-24090172/Source1/Zone1'].attrs['Extent'][1])
print("\n")

