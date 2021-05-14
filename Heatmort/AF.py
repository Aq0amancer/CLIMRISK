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
rcp_scenario=sys.argv[1] # get regression type from bash
ssp_scenario=sys.argv[2] # get regression type from bash
tas_percentil=sys.argv[3]
uhi=sys.argv[4]

def AF(rcp_scenario, ssp_scenario, tas_percentil, uhi):
    '''
    This function takes apparent temperature (AT) estimates and generates the fraction of deaths attributable to heat (AF)
    '''
    baccini_data = scipy.io.loadmat(path+'/Masks/baccini_matrix_acclimatized_'+rcp_scenario +'_'+ ssp_scenario+'_'+ tas_percentil+'pctl_'+ uhi +'.mat') # data for thresholds, with acclimatization
    #h=baccini_data['baccini_matrix_acclimatized']
    #b=baccini_data['baccini_variance']
    #AF_all=np.empty((80,90,134))
    for date in AF_dates:
        year=int(date[0:4]) #get first year from the date string
        for year_value in range(year,year+5):
            with xr.open_dataset(path+'/CLIMRISK temperatures/AT/'+rcp_scenario+'/AT_' + rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.nc') as climate_data:
                h=baccini_data['baccini_matrix_acclimatized'][:,:,year_value-2021]
                b=baccini_data['baccini_variance']
                climate_data_year=climate_data.sel(time=str(year_value))
                AT=climate_data_year['apparent_tas'] # import AT
                #print(np.nanmax(AT))
                #print(baccini_matrix.shape)
                #at_boolean=np.greater(AT,h) # is the temperature above
                #AF=1-(1/(np.exp(b*(AT-h)*at_boolean)))
                AF=1-(1/(np.exp(b*(AT-h))))
                AF=AF.clip(min=0)
                if year_value == year:
                    AF_date=AF
                else:
                    AF_date=np.concatenate((AF_date,AF),axis=0)
                #print(AF_date.shape)
        AF_date = xr.DataArray(AF_date, coords={'lat': climate_data['lat'], 'lon': climate_data['lon'], 'time': climate_data['time']}, dims=["time", "lat", "lon"])
        climate_data=climate_data.assign(attributable_fraction=AF_date)
        # Generate average AF
        year = int(date[0:4])  # get first year from the date string
        AF_year=np.empty((5,90,134))
        for index,year_value in enumerate(range(year, year+5)):
            AF_year[index,:,:] = np.mean(climate_data['attributable_fraction'].sel(time=slice(str(year_value)+'-4', str(year_value)+'-9')), axis=0)
            #print(np.nanmax(AF_year))
        if date == '20210101-20251231':
            AF_all=AF_year
        else:
            AF_all=np.concatenate((AF_all,AF_year),axis=0)
            #climate_data.close()
    # Save for matlab
    AF_dict={"AF": AF_all}
    scipy.io.savemat(path+'/AF_' + rcp_scenario +
                    '_' + ssp_scenario + '_' + tas_percentil + 'th_2021-2100_' + uhi + '.mat', AF_dict)
    #climate_data.to_netcdf(path+'/CLIMRISK temperatures/AT/'+rcp_scenario+'/AF_' + rcp_scenario +
    #                       '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_' + uhi + '.nc')
    return AF

# Run function
AF(rcp_scenario, ssp_scenario, tas_percentil, uhi)
