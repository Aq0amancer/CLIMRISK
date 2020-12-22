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
import statsmodels.api as sm
from statsFunc import crossValidateKfold
from pathCORDEX import *
import time


""" Try loading less data so that it fits into the matrix.
    Need to make functions per month, check how well it does.
"""
# Parameters
folds= 5
year_begin=2010
year_end=2010

number_of_months=(year_end-year_begin+1)*12

coef=np.zeros((90,134,2))
adjr2=np.zeros((number_of_months,90,134))
rmse=np.zeros((number_of_months,90,134))
month_count=0 #start counting months

for year in range(year_begin,year_end+1):
    for month in range(1,13):
        tas_all_month=[]
        hurs_all_month=[]
        start = time.time()
        for gcm in gcms:
            for rcp in rcps:
                for rp in rps:
                    for rcm in rcms:
                        for version in versions:
                            # Load data
                            try:
                                tas=month_load(CORDEX_path,mohc_dates,most_dates,years,'tas',gcm,rcp,rp,rcm,version,str(year),str(month))
                                hurs=month_load(CORDEX_path,mohc_dates,most_dates,years,'hurs',gcm,rcp,rp,rcm,version,str(year),str(month))
                                # Concatenate
                                if any(tas_all_month):
                                    tas_all_month=xr.concat([tas_all_month, tas], dim="time")
                                else:
                                    tas_all_month=tas
                                if any(hurs_all_month):
                                    hurs_all_month=xr.concat([hurs_all_month, hurs], dim="time")
                                else:
                                    hurs_all_month=hurs
                            except Exception as e:
                                #print('Concat loop: ' + str(e))
                                pass
        #print(tas_all_month.sizes)
        for lat in range(90):
            for lon in range(134):
                tas_cell_month=tas_all_month['tas'][:,lat,lon]
                hurs_cell_month=hurs_all_month['hurs'][:,lat,lon]
                try:
                    coef[lat,lon,:],adjr2[month-1,lat,lon],rmse[month-1,lat,lon]=crossValidateKfold(tas_cell_month,hurs_cell_month,folds)
                except Exception as e:
                    print('K-fold loop: ' + str(e))
                    #pass
        month_count=month_count+1 # increment month
        end = time.time()
        print(str(month) + '/' + str(year) + ' finished in ' + str(end - start) + ' seconds')


# Load monthly time mask
monthly_mask = xr.open_dataset("monthly_time.nc")

# Convert adjr2 and rmse data to xarray.Dataset format
ds = xr.Dataset(
    data_vars=dict(
        adjr2=(["time", "lat", "lon"], adjr2),
        rmse=(["time", "lat", "lon"], rmse),
    ),
    coords=dict(
        lon=(['lon'], hurs_all_month['lon']),
        lat=(["lat"], hurs_all_month['lat']),
        time=monthly_mask['time'][(year_begin-2006)*12:(year_end+1-2006)*12],
    ),
    attrs=dict(description="Monthly Adj. R^2 and RMSE results for tas/hurs relationships."))

# Save to NCDF4
ds.to_netcdf("test_output.nc")