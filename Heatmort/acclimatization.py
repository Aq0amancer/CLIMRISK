"""
--------------------------------
CLIMRISK Model. Heatmort module. Acclimatization function.
--------------------------------
Presents the main workflow for calculating the:
    1. Mean monthly temperature from daily temepratures (CLIMRISK + CORDEX)
    2. Change in monthly temperatures
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

def acclimatization(rcp_scenario, ssp_scenario, tas_percentil, uhi):
    index=0
    for date in AF_dates: # First, concatenate mean monthly temperatures for all dates
        mean_summer_temperatures_date=meanSummerTemperatures(path,date,rcp_scenario, ssp_scenario, tas_percentil,uhi)
        # Calculate the difference in mean summer temperatures
        year=int(date[0:4]) #get first year from the date string
        for year_index in range(5):
            index=index+year_index
            if index==0:
                mean_summer_temperatures_date_diff=np.zeros((90,134))
            else:
                mean_summer_temperatures_date_diff=np.dstack((mean_summer_temperatures_date_diff,np.squeeze(mean_summer_temperatures_date[year_index,:,:]-mean_summer_temperatures_date[year_index-1,:,:])))
    # Shuffle dimensions around to fit NC standard (time,lat,lon)
    mean_summer_temperatures_date_diff=np.transpose(mean_summer_temperatures_date_diff, (2, 0, 1))
    print(mean_summer_temperatures_date_diff.shape)
    template_file = path + '/Masks/year_template/year_template.nc'
    with xr.open_dataset(template_file) as yearly_mask:
    #Convert adjr2 and rmse data to xarray.Dataset format
        ds = xr.Dataset(
        data_vars=dict(
            diff_mean_summer_temperature=(["time", "lat", "lon"], mean_summer_temperatures_date_diff),
            time_bnds=(["time", "bnds"], yearly_mask['time_bnds'])
        ),
        coords=dict(
            lon=(['lon'], yearly_mask['lon']),
            lat=(["lat"], yearly_mask['lat']),
            time=yearly_mask['time'],
        ),
        attrs={'description': "Year-on-year differences in monthly mean estimates of surface air temperature based on CORDEX patterns and CLIMRISK annual 0.5*0.5 degree annual mean temperature estimates.",
            'Climate scenario':rcp_scenario,
            'Socioeconomic scenario(for UHI)': ssp_scenario,
            'Temperature realization percentile':(str(tas_percentil)+'th'),
            'Urban Heat Island(UHI)':uhi})

        # Save to NCDF4
        ds.to_netcdf(path + '/CLIMRISK temperatures/Mean_monthly_tas_' + rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + uhi + '.nc')

acclimatization(rcp_scenario, ssp_scenario, tas_percentil, uhi)