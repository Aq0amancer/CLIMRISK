"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Presents the main workflow for calculating the:
    1. Dew point from relative humidity (%) and temperature (C)
    2. Apparent temperature (AT) from dew point estimates
    3. Attributable deaths (AD) from AT.
"""

import netCDF4 as nc
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
from IO_functions import *
from parameters import *
import scipy.io
#import statsmodels.api as sm
from sklearn import neighbors
#from statsFunc import crossValidateKfold
from pathCORDEX import *
from statsFunc import magnus
import time
import sys

# Bash parameters
date=sys.argv[1] # get first year argument from bash
rcp_scenario=sys.argv[2] # get regression type from bash
ssp_scenario=sys.argv[3] # get regression type from bash
tas_percentil=sys.argv[4]
uhi=sys.argv[5]

def heatMort(date,rcp_scenario, ssp_scenario, tas_percentil,uhi):
    # Load data
    climate_data=loadClimate(climate_data_path,date,rcp_scenario, ssp_scenario, tas_percentil,uhi)
    lat_range=90
    lon_range=134
    time_range=len(climate_data['time'])
    dew=np.zeros((time_range,lat_range,lon_range))
    # Magnus formula for dew points
    for lat in range(lat_range): #90
        for lon in range(lon_range): #134
            for day in range(1): # for every day, do KNN regression
                dew[day,lat,lon]=magnus(climate_data['daily_climrisk_tas'][day,lat,lon],climate_data['daily_climrisk_hurs'][day,lat,lon])

# Run function
heatMort(date,rcp_scenario, ssp_scenario, tas_percentil,uhi)