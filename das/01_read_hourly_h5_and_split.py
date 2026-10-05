# ################################ to edit ######################################
###############################################################################
#
# Experiment name (DO NOT MODIFY):
EXP_NAME="DAS_INGV_08"                 
#
# Name of the event (i.e. TAP_TEST_01) THIS LABEL WILL BE INCLUDED IN ALL FILES
EV_NAME="ERUPTION_01"  
#
# Directory where the raw data are stored in:
#RawDataDir="/Users/nicola/Desktop/DAS-INGV-08-repo/"
RawDataDir="/home/dario/Documenti/das_nicola/mission_2026_giu/das_data/"
#
#OUTPUT DIR
output_dirName="./"
output_fileName=output_dirName + "DAS-h5/" + EXP_NAME + "__" + EV_NAME + ".h5"
output_figure=output_dirName + "DAS-plots/" + EXP_NAME + "__" + EV_NAME + ".png"
#
#
# SELECT CABLE SECTIONS to extract data from (IN METERS, not in channels):
startDistance=0
endDistance=800



# ANALYSED DATA:

if EV_NAME == "ERUPTION_01":
    fileName= RawDataDir + "DAS_INGV_08_2026-06-30_19-00-54_UTC.h5"
    startMinute=0.0    # Minutes of the first tap in teh sequence of three taps
    startSecond=0.0    # Seconds of the first tap in teh sequence of three taps
    nTaps=1            # Number of Taps in teh tap-test
    deltaTap=5.0      # Inter-time between taps (in seconds)
    preEvent=0.0      # Seconds BEFORE the first tap
    postEvent=58.0     # Seconds BEFORE the first tap
    startTapData = (startMinute*60) + startSecond - preEvent
    Duration= preEvent + (nTaps-1)*deltaTap + postEvent
    
 
    
print(" -> Selecting data for event:", EV_NAME)
print(" -> H5 FILE: ", fileName)
print(" -> Starting from: ", startTapData, " seconds from the beginning of the file") 
print(" -> Ending after: ", Duration, " seconds") 



# Edit only if you think you are a Pro python-user

modePro="StrainRate"  #StrainRate or Strain  
timeType='timeStamp'  # second or timeStamp

#Display parameters
limMin=-200
limMax=200
cmap='RdBu'


###############################################################################

###############################################################################
################################ Libraries ###################################
###############################################################################
import h5py
import numpy as np
from datetime import datetime, timezone
#For built-in function created by Febus
from febus_optics_lib.reader import H5ReaderDas
#from febus_read_write_h5 import plotMatrix
##############################################################################
#Read DAS interrogator serial number
with h5py.File(fileName, "r") as f:
    # List all groups
    print("Keys: %s" % f.keys())

with h5py.File(fileName, 'r') as f:
    time_das = np.array(f['fa1-24090172/Source1/time'])
    print('START EPOCH for the full H5 file:', time_das[0])
    print('END EPOCH for the full H5 file:', time_das[time_das.shape[0]-1])    
    
# SET TIME SECTION IN H5 file to extract data from

    startTime=int(time_das[0]) + startTapData           # start time to process   
    endTime=startTime+Duration                          # end time to process