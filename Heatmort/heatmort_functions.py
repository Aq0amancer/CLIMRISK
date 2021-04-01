"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Presents the main workflow for calculating the:
    1. Dew point from relative humidity (%) and temperature (C)
    2. Apparent temperature (AT) from dew point estimates
    3. Attributable deaths (AD) from AT.
"""
import math
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
from paths import *
from statsFunc import magnus
import time
import sys

# Bash parameters
date=sys.argv[1] # get first year argument from bash
rcp_scenario=sys.argv[2] # get regression type from bash
ssp_scenario=sys.argv[3] # get regression type from bash
tas_percentil=sys.argv[4]
uhi=sys.argv[5]

def AT(date,rcp_scenario, ssp_scenario, tas_percentil,uhi):
    # Load data
    climate_data=loadClimate(path +'/CLIMRISK temperatures/',date,rcp_scenario, ssp_scenario, tas_percentil,uhi)
    # Magnus formula for dew points
    dew=magnus(climate_data['daily_climrisk_tas'],climate_data['daily_climrisk_hurs'])
    climate_data=climate_data.assign(dew_point=dew)
    # Apparent temperatures
    AT= -2.653 + 0.994*climate_data['daily_climrisk_tas'] + 0.0153*np.square(climate_data['dew_point'])
    climate_data=climate_data.assign(apparent_tas=AT)
    # Save dew point to current .NC file
    AT_dict={"AT": AT} #G
    scipy.io.savemat(path+'/AT_' + rcp_scenario +
                    '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.mat', AT_dict)
    climate_data.to_netcdf('AT_'+ rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_'+ uhi + '.nc')
    return AT


def AF(date, rcp_scenario, ssp_scenario, tas_percentil, uhi):
    '''
    This function takes apparent temperature (AT) estimates and generates the fraction of deaths attributable to heat (AF)
    '''
    climate_data=xr.open_dataset(path+'/CLIMRISK temperatures/AT/'+rcp_scenario+'/AT_' + rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.nc')
    AT=climate_data['apparent_tas'] # import AT
    baccini_data = scipy.io.loadmat(path+'/Masks/baccini_matrix.mat')
    h=baccini_data['baccini_matrix']
    b=baccini_data['baccini_variance']
    #print(baccini_matrix.shape)
    #at_boolean=np.greater(AT,h) # is the temperature above
    #AF=1-(1/(np.exp(b*(AT-h)*at_boolean)))
    AF=1-(1/(np.exp(b*(AT-h))))
    AF=AF.clip(min=0)
    climate_data=climate_data.assign(attributable_fraction=AF)
    # Generate average AF
    year = int(date[0:4])  # get first year from the date string
    AF_year=np.empty((5,90,134))
    for index,year_value in enumerate(range(year, year+5)):
        AF_year[index,:,:] = np.mean(climate_data['attributable_fraction'].sel(time=slice(str(year_value)+'-4', str(year_value)+'-9')), axis=0)
    # Save for matlab
    AF_dict={"AF": AF_year}
    scipy.io.savemat(path+'/AF_' + rcp_scenario +
                     '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.mat', AF_dict)
    #climate_data.to_netcdf(path+'/CLIMRISK temperatures/AT/'+rcp_scenario+'/AF_' + rcp_scenario +
    #                       '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.nc')
    return AF
    
def AD():
    '''
    Attributable deaths function.
    Takes in population estimates from CLIMRISK, multiplies by the crude mortality rate (r), the fraction of deaths between April - September and the fraction of deaths due to heat (AF)
    r - average annual crude country-level mortality rate for a period
    '''
    lambdah=0.45 # PHEWE proportion of annual deaths during the warm season
    pop=0
    AD=AF*pop*r*lambdah

# Run function
#apparent_temperatures=AT(date,rcp_scenario, ssp_scenario, tas_percentil,uhi) 
AT(date, rcp_scenario, ssp_scenario, tas_percentil, uhi)
