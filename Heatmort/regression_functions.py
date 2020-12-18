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

""" Try loading less data so that it fits into the matrix.
    Need to make functions per month, check how well it does.
"""
# Parameters
folds= 10
coef=np.zeros((90,134,2))
adjr2=np.zeros((90,134))
rmse=np.zeros((90,134))

for year in range(2010,2100):
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
                                    hurs_all_month=xr.concat([hurs_all_month, hurs], dim="time")
                                else:
                                    tas_all_month=tas
                                    hurs_all_month=hurs
                            except Exception as e: 
                                pass
        
        # Regression
        # Might have to do per cell
        for lat in range(90):
            for lon in range(134):
                tas_cell_month=tas_all_month['tas'][:,lat,lon]
                hurs_cell_month=hurs_all_month['hurs'][:,lat,lon]
                try:
                    coef[lat,lon,:],adjr2[lat,lon],rmse[lat,lon]=crossValidateKfold(tas_cell_month,hurs_cell_month,10)  
                    print(str(month) + '/' + str(year) + ' finished')     
                except Exception as e: 
                    #print(e)
                    pass

