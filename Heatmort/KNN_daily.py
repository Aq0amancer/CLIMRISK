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
tas_percentile=75 # Climate sensitivity parameter
daily_climrisk_hurs=np.zeros((1825,90,134))
daily_climrisk_tas=np.zeros((1825,90,134))

# Bash parameters
year_begin=int(sys.argv[1]) # get first year argument from bash
year_end=int(sys.argv[2]) # get last year argument from bash
rcp_scenario=sys.argv[3] # get regression type from bash
tas_percentil=sys.argv[4]
# KNN setup
n_neighbors=2 # number of nearest-neighbours
weights= 'distance' # can also be 'uniform'
knn = neighbors.KNeighborsRegressor(n_neighbors, weights=weights)


def KNNRegression(year_begin,year_end,rcp_scenario, tas_percentil):
    start = time.time()
    # Load CLIMRISK annual temperature data
    climrisk_tas = scipy.io.loadmat('CLIMRISK_'+rcp_scenario+'_SSP1_IIASA_50pctl_50climsens.mat')['TEMPERATURES_FINAL'] # Load CLIMRISK annual temperatures 
    for year in range(year_begin,year_end+1):
        tas_all_year=[]
        hurs_all_year=[]
        for gcm in gcms:
            for rcp in rcps:
                for rp in rps:
                    for rcm in rcms:
                        for version in versions:
                            # Load data
                            try:
                                tas=year_load(CORDEX_path,mohc_dates,most_dates,years,'tas',gcm,rcp,rp,rcm,version,str(year)).expand_dims({'obs':1}) # Expand the dimension for observations
                                hurs=year_load(CORDEX_path,mohc_dates,most_dates,years,'hurs',gcm,rcp,rp,rcm,version,str(year)).expand_dims({'obs':1})
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
        patterns_path=str(year_begin) +'-'+ str(year_end) + '_tas_patterns.nc'
        patterns_dataset = xr.open_dataset(patterns_path)
        for lat in range(90):
            for lon in range(134):
                daily_climrisk_tas=patterns2tas(patterns_dataset,year_begin,year_end,climrisk_tas,tas_percentile,lat,lon)
                for day in range(1825): # for every day, do KNN regression
                    tas_cell_day_train=tas_all_year['tas'][:,day,lat,lon]
                    hurs_cell_day_train=hurs_all_year['hurs'][:,day,lat,lon]
                    tas_cell_day_train=np.vstack(np.array(tas_cell_day_train,dtype=np.float64))
                    hurs_cell_day_train=np.vstack(np.array(hurs_cell_day_train,dtype=np.float64))
                    try: # Try KNN
                        daily_climrisk_hurs[day,lat,lon] = knn.fit(tas_cell_day_train, hurs_cell_day_train).predict(daily_climrisk_tas[day])
                    except Exception as e:
                        #print('K-fold loop: ' + str(e))
                        pass
        end = time.time()
        print(str(year) + ' finished in ' + str(end - start) + ' seconds')

# Load monthly time mask
with xr.open_dataset("template.nc") as monthly_mask:
# Convert adjr2 and rmse data to xarray.Dataset format
    ds = xr.Dataset(
        data_vars=dict(
            daily_climrisk_hurs=(["time", "lat", "lon"], daily_climrisk_hurs[(year_begin-2006)*12:(year_end+1-2006)*12,:,:]),
            daily_climrisk_tas=(["time", "lat", "lon"], daily_climrisk_tas[(year_begin-2006)*12:(year_end+1-2006)*12,:,:]),
            time_bnds=(["time", "bnds"], monthly_mask['time_bnds'][(year_begin-2006)*12:(year_end+1-2006)*12])
        ),
        coords=dict(
            lon=(['lon'], monthly_mask['lon']),
            lat=(["lat"], monthly_mask['lat']),
            time=monthly_mask['time'][(year_begin-2006)*12:(year_end+1-2006)*12],
        ),
        attrs=dict(description="Daily estimates for TAS and HURS originating from CLIMRISK. Method used = KNN with"))

    # Save to NCDF4
    ds.to_netcdf(str(year_begin)+ '-' + str(year_end) + "_test_output.nc")


KNNRegression(year_begin,year_end,rcp_scenario, tas_percentil)