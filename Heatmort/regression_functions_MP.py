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
import sys

# Bash parameters
year_begin=int(sys.argv[1]) # get first year argument from bash
year_end=int(sys.argv[2]) # get last year argument from bash
reg_type=sys.argv[3] # get regression type from bash

def runRegressions(year_begin,year_end,reg_type):

    if reg_type=='first order':
        formula='y ~ x'
        number_of_coefs=1
    elif reg_type=='second order':
        formula='y ~ I(x**2) + x'
        number_of_coefs=2
    
    folds= 2 #number of folds for
    number_of_months=(year_end-year_begin+1)*12
    coef=np.zeros((number_of_months,90,134,number_of_coefs))
    adjr2=np.zeros((number_of_months,90,134))
    rmse=np.zeros((number_of_months,90,134))
    month_count=0 #start counting months

    for year in range(year_begin,year_end+1):
        for month in range(1,13):
            tas_all_month=[]
            hurs_all_month=[]
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
            start = time.time()
            for lat in range(90):
                for lon in range(134):
                    tas_cell_month=tas_all_month['tas'][:,lat,lon]
                    hurs_cell_month=hurs_all_month['hurs'][:,lat,lon]
                    tas_cell_month=np.vstack(np.array(tas_cell_month,dtype=np.float64))
                    hurs_cell_month=np.vstack(np.array(hurs_cell_month,dtype=np.float64))
                    #print(tas_cell_month.shape)
                    try:
                        adjr2[month_count,lat,lon],rmse[month_count,lat,lon]=crossValidateKfold(tas_cell_month,hurs_cell_month,number_of_coefs,reg_type,folds,stratified='No')
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
                lon=(['lon'], hurs_all_month['lon']),
                lat=(["lat"], hurs_all_month['lat']),
                time=monthly_mask['time'][(year_begin-2006)*12:(year_end+1-2006)*12],
            ),
            attrs=dict(description="Monthly Adj. R^2 and RMSE results for tas/hurs relationships."))

        # Save to NCDF4
        ds.to_netcdf(str(year_begin)+ '-' + str(year_end) + "_test_output.nc")


runRegressions(year_begin,year_end,reg_type)