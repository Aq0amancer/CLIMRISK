"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Presents the KNN algorithm for predicting daily CORDEX relative humidity using annual surface annual temperatures for any scenario
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
import time
import sys

# General parameters
tas_percentile=50 # Climate sensitivity parameter

# Bash parameters
date=sys.argv[1] # get first year argument from bash
rcp_scenario=sys.argv[2] # get regression type from bash
ssp_scenario=sys.argv[3] # get regression type from bash
tas_percentil=sys.argv[4]
uhi=sys.argv[5]

# KNN setup
n_neighbors=2 # number of nearest-neighbours
weights= 'distance' # can also be 'uniform'
knn = neighbors.KNeighborsRegressor(n_neighbors, weights=weights)


def KNNRegression(date,rcp_scenario, ssp_scenario, tas_percentil,uhi):
    start = time.time()
    # Load CLIMRISK annual temperature data
    climrisk_tas = scipy.io.loadmat(climrisktemp_path+'CLIMRISK_'+rcp_scenario+'_'+ssp_scenario+'_IIASA_50pctl_50climsens_' + uhi + '.mat')['TEMPERATURES_FINAL'] # Load CLIMRISK annual temperatures 
    tas_all_year=[]
    hurs_all_year=[]
    for gcm in gcms:
        for rcp in rcps:
            for rp in rps:
                for rcm in rcms:
                    for version in versions:
                        # Load data
                        try:
                            tas=load(CORDEX_path,'tas',gcm,rcp,rp,rcm,version,date).expand_dims({'obs':1}) # Expand the dimension for observations
                            hurs=load(CORDEX_path,'hurs',gcm,rcp,rp,rcm,version,date).expand_dims({'obs':1}) # Expand the dimension for observations
                            # Concatenate
                            if any(tas_all_year):
                                tas_all_year=xr.concat([tas_all_year, tas], dim="obs")
                            else:
                                tas_all_year=tas
                            if any(hurs_all_year):
                                hurs_all_year=xr.concat([hurs_all_year, hurs], dim="obs")
                            else:
                                hurs_all_year=hurs
                        except Exception as e:
                            #print('Concat loop: ' + str(e))
                            pass
    #print(tas_all_year.sizes)
    # Loat patterns
    patterns_full_path=patterns_path + date + '_tas_patterns.nc'
    patterns_dataset = xr.open_dataset(patterns_full_path)
    count=0
    # Dimensions
    lat_range=90
    lon_range=134
    time_range=len(tas_all_year['time'])
    # Initialize
    daily_climrisk_hurs=np.zeros((time_range,90,134))
    daily_climrisk_tas=np.zeros((time_range,90,134))
    daily_climrisk_tas=patterns2tas(patterns_dataset,date,climrisk_tas,tas_percentile)
    #print(daily_climrisk_tas)
    for lat in range(lat_range): #90
        for lon in range(lon_range): #134
            for day in range(time_range): # for every day, do KNN regression
                tas_cell_day_train=np.asarray(tas_all_year['tas'][:,day,lat,lon].dropna("obs")).reshape(-1,1)
                hurs_cell_day_train=np.asarray(hurs_all_year['hurs'][:,day,lat,lon].dropna("obs")).reshape(-1,1)
                tas_cell_day_train=np.vstack(np.array(tas_cell_day_train,dtype=np.float64))
                hurs_cell_day_train=np.vstack(np.array(hurs_cell_day_train,dtype=np.float64))
                try: # Try KNN
                    daily_climrisk_hurs[day,lat,lon] = knn.fit(tas_cell_day_train, hurs_cell_day_train).predict(np.asarray(daily_climrisk_tas[day,lat,lon]).reshape(-1,1))
                except Exception as e:
                    #print('K-fold loop: ' + str(e))
                    pass
            count+=1
            print(str(round(count*100/(lat_range*lon_range),2)) + '% complete')
    end = time.time()
    print(date + ' finished in ' + str(end - start) + ' seconds')
    # Load monthly time mask
    with xr.open_dataset(date+'_template.nc') as monthly_mask:
    #Convert adjr2 and rmse data to xarray.Dataset format
        ds = xr.Dataset(
        data_vars=dict(
            daily_climrisk_hurs=(["time", "lat", "lon"], daily_climrisk_hurs),
            daily_climrisk_tas=(["time", "lat", "lon"], daily_climrisk_tas),
            time_bnds=(["time", "bnds"], monthly_mask['time_bnds'])
        ),
        coords=dict(
            lon=(['lon'], monthly_mask['lon']),
            lat=(["lat"], monthly_mask['lat']),
            time=monthly_mask['time'],
        ),
        attrs={'description': "Daily estimates of surface air temperature and relative humidity based on CORDEX patterns and CLIMRISK annual 0.5*0.5 degree annual mean temperature estimates. Method used = KNN with " +str(n_neighbors) + " nearest neighbours.",
            'Climate scenario':rcp_scenario,
            'Socioeconomic scenario(for UHI)': ssp_scenario,
            'Temperature realization percentile':(str(tas_percentil)+'th'),
            'Urban Heat Island(UHI)':uhi})

        # Hurs
        ds['daily_climrisk_hurs'].attrs['standard_name'] = 'humidity'
        ds['daily_climrisk_hurs'].attrs['long_name'] = 'Near-Surface Relative Humidity'
        ds['daily_climrisk_hurs'].attrs['units'] = '%'
        ds['daily_climrisk_hurs'].attrs['cell_methods']='time: mean'
        # Tas
        ds['daily_climrisk_tas'] = ds['daily_climrisk_tas']-272.15
        ds['daily_climrisk_tas'].attrs['standard_name'] = 'temperature'
        ds['daily_climrisk_tas'].attrs['long_name'] = 'Near-Surface Air Temperature'
        ds['daily_climrisk_tas'].attrs['units'] = 'degrees C'
        ds['daily_climrisk_tas'].attrs['cell_methods']='time: mean'

    # Save to NCDF4
    ds.to_netcdf(rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_'+ uhi + '.nc')


KNNRegression(date,rcp_scenario, ssp_scenario, tas_percentil,uhi)