
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

def mergeTasPatterns(year_begin,year_end):
    
    for year in range(year_begin,year_end+1):
        tas_all_year=[]
        for gcm in gcms:
            for rcp in rcps:
                for rp in rps:
                    for rcm in rcms:
                        for version in versions:
                            # Load data
                            try:
                                tas=year_load_patterns(CORDEX_path,mohc_dates,most_dates,years,'tas',gcm,rcp,rp,rcm,version,str(year)).expand_dims({'obs':1}) # Expand the dimension for observations
                                # Concatenate
                                if any(tas_all_year):
                                    tas_all_year=xr.concat([tas_all_year, tas], dim="obs")
                                else:
                                    tas_all_year=tas
                            except Exception as e:
                            #print('K-fold loop: ' + str(e))
                                pass

    tas=year_load_patterns(CORDEX_path,mohc_dates,most_dates,years,'tas','ICHEC-EC-EARTH','rcp85','r12i1p1','SMHI-RCA4','v1','2006')
    ds = xr.Dataset(
        data_vars=dict(
            tas_patterns=(["obs","time", "lat", "lon"], tas_all_year['tas']),
            time_bnds=(["time", "bnds"], tas['time_bnds'])
        ),
        coords=dict(
            lon=(['lon'], tas['lon']),
            lat=(["lat"], tas['lat']),
            time=tas['time'],
        ),
        attrs=dict(description="Temperature patterns for" + str(year_begin)+ '-' + str(year_end)))

    # Save to NCDF4
    ds.to_netcdf(str(year_begin)+ '-' + str(year_end) + "_tas_patterns.nc")

mergeTasPatterns(year_begin,year_end)