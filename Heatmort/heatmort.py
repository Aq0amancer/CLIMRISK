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
    # Magnus formula for dew points
    dew=magnus(climate_data['daily_climrisk_tas'],climate_data['daily_climrisk_hurs'])
    climate_data=climate_data.assign(dew_point=dew)
    # Apparent temperatures
    AT= -2.653 + 0.994*climate_data['daily_climrisk_tas'] + 0.0153*np.square(climate_data['dew_point'])
    climate_data=climate_data.assign(apparent_tas=AT)
    # Save dew point to current .NC file
    climate_data.to_netcdf('AT_'+ rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_'+ uhi + '.nc')
# Run function
heatMort(date,rcp_scenario, ssp_scenario, tas_percentil,uhi)