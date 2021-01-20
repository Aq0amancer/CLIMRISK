"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Contains functions for regressions of temperature and relative humidity of the CORDEX dataset.
"""

import netCDF4 as nc
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
from IO_functions import *
from parameters import *
#import statsmodels.api as sm
from sklearn import neighbors
#from statsFunc import crossValidateKfold
from pathCORDEX import *
import time
import sys

# Bash parameters
year_begin=int(sys.argv[1]) # get first year argument from bash
year_end=int(sys.argv[2]) # get last year argument from bash
reg_type=sys.argv[3] # get regression type from bash

# Setup nearest-neighbours function
knn = neighbors.KNeighborsRegressor(n_neighbors, weights=weights)

def runRegressions(year_begin,year_end,reg_type):

    if reg_type=='first order':
        formula='y ~ x'
        number_of_coefs=1
    elif reg_type=='second order':
        formula='y ~ I(x**2) + x'
        number_of_coefs=2
    
    number_of_months=(year_end-year_begin+1)*12
    month_count=0 #start counting months

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
        start = time.time()
        for lat in range(90):
            for lon in range(134):
                for day in range(1825): # for every day, do KNN regression
                    tas_cell_day_train=tas_all_year['tas'][:,day,lat,lon]
                    hurs_cell_day_train=hurs_all_year['hurs'][:,day,lat,lon]
                    tas_cell_day_train=np.vstack(np.array(tas_cell_day_train,dtype=np.float64))
                    hurs_cell_day_train=np.vstack(np.array(hurs_cell_day_train,dtype=np.float64))
                    try: # Try KNN
                        y_ = knn.fit(tas_cell_day_train, hurs_cell_day_train).predict(tas_cell_day_CLIMRISK)
                    except Exception as e:
                        #print('K-fold loop: ' + str(e))
                        pass

        month_count=month_count+1 # increment month
        end = time.time()
        print(str(month) + '/' + str(year) + ' finished in ' + str(end - start) + ' seconds')

# Load monthly time mask
with xr.open_dataset("merged_monthly.nc") as monthly_mask:
# Convert adjr2 and rmse data to xarray.Dataset format
    ds = xr.Dataset(
        data_vars=dict(
            adjr2=(["time", "lat", "lon"], adjr2),
            rmse=(["time", "lat", "lon"], rmse),
            time_bnds=monthly_mask['time_bnds']
        ),
        coords=dict(
            lon=(['lon'], hurs_all_year['lon']),
            lat=(["lat"], hurs_all_year['lat']),
            time=monthly_mask['time'][(year_begin-2006)*12:(year_end+1-2006)*12],
        ),
        attrs=dict(description="Monthly Adj. R^2 and RMSE results for tas/hurs relationships."))

    # Save to NCDF4
    ds.to_netcdf(str(year_begin)+ '-' + str(year_end) + "_test_output.nc")


runRegressions(year_begin,year_end,reg_type)