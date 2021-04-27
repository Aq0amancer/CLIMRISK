"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Contains functions for reading and writing files of the CORDEX dataset.
"""

import netCDF4 as nc
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
from paths import * # Import path to CORDEX data
from numpy import array
def saveReg(relative_path,coefs,adjr2,rmse):
    np.savetxt(relative_path + "corrMatrix_EUR-11_"+ gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".csv", corrMatrix, delimiter=",")
    print('Successful save: corrMatrix-' + gcm + '-' + rcp + '-' + rp + '-' + version + '-' + date) # Print info

def load(relative_path,var,gcm,rcp,rp,rcm,version,date):
    """
    This function loads the data from CORDEX for a given
    1. GCM
    2. RCP scenario
    3. RP
    4. Version
    5. 5-year interval (between 2006 - 2100)
    """
    data_path = relative_path + "/" + gcm + "/" + var + "/" + rcp + "/remapped_" + var + "_EUR-11_" + gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".nc"
    try:
        data = xr.open_dataset(data_path)
        print("Successful load: "+ data_path)
    except Exception as e: 
        #print(e)
        data=[]

    return data

def loadClimate(relative_path,date,rcp_scenario, ssp_scenario, tas_percentil,uhi):
    # Load temperature and relative humidity data from CLIMRISK + CORDEX
    data_path = relative_path + "/CLIMRISK temperatures/" + rcp_scenario + '/'+ rcp_scenario + '_' + ssp_scenario + '_' + tas_percentil + 'th_' + date + '_'+ uhi + '.nc'
    data = xr.open_dataset(data_path)
    print("Successful load: "+ data_path)
    return data


def month_load(relative_path,mohc_dates,most_dates,years,var,gcm,rcp,rp,rcm,version,year,month):
    
    """
    This function loads the data from CORDEX for a given month
    """
    if gcm=='MOHC-HadGEM2-ES': # MohC has a different labelling for the dates
        date=mohc_dates[np.where((years==year))[0][0]] # Index the correct file, corresponding to year
    else:
        date=most_dates[np.where((years==year))[0][0]]
    data_path = relative_path + "/" + gcm + "/" + var + "/" + rcp + "/remapped_" + var + "_EUR-11_" + gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".nc"
                    
    try:
        data = xr.open_dataset(data_path)
        data=data.sel(time=year + "-" + month)
        #print("Successful load: "+ data_path)
    except Exception as e: 
        #print(e)
        data=[]

    return data
    
def year_load_patterns(relative_path,var,gcm,rcp,rp,rcm,version,date):
    
    """
    This function loads the data from CORDEX for a given month
    """
    data_path = relative_path + "/" + gcm + "/" + var + "/" + rcp + "/remapped_" + var + "_patterns_EUR-11_" + gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".nc"        
    try:
        data = xr.open_dataset(data_path)
        #print("Successful load: "+ data_path)
    except Exception as e: 
        #print(e)
        data=[]

    return data

def year_load(relative_path,mohc_dates,most_dates,years,var,gcm,rcp,rp,rcm,version,year):
    
    """
    This function loads the data from CORDEX for a given month
    """
    if gcm=='MOHC-HadGEM2-ES': # MohC has a different labelling for the dates
        date=mohc_dates[np.where((years==year))[0][0]] # Index the correct file, corresponding to year
    else:
        date=most_dates[np.where((years==year))[0][0]]
    data_path = relative_path + "/" + gcm + "/" + var + "/" + rcp + "/remapped_" + var + "_patterns_EUR-11_" + gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".nc"
                    
    try:
        data = xr.open_dataset(data_path)
        data=data.sel(time=year)
        print("Successful load: "+ data_path)
    except Exception as e: 
        #print(e)
        data=[]

    return data

def patterns2tas(patterns_dataset,date,annual_tas,percentile):
    # Open the patterns dataset
    #patterns_array = np.percentile(patterns_dataset['tas'], percentile,axis=0) # return a percentile
    year=int(date[0:4]) #get first year from the date string
    annual_tas = np.transpose(annual_tas, (2, 0, 1))
    annual_tas=annual_tas+273.15
    for year_value in range(year,year+5):
        patterns_array=patterns_dataset['tas'].sel(time=str(year_value)).dropna('obs') 
        patterns_array_year = np.percentile(patterns_array, percentile,axis=0) # return a percentile
        daily_tas_year=annual_tas[year_value-2010,:,:] * patterns_array_year
        if year_value==year:
            daily_tas_all=daily_tas_year
        else:
            daily_tas_all=np.concatenate((daily_tas_all,daily_tas_year),axis=0)  # For each year, multiply patterns_array (365,90,134) with the CLIMRISK annual temperatures (90,134,1)
    return daily_tas_all

def meanSummerTemperatures(relative_path,date,rcp_scenario, ssp_scenario, tas_percentil,uhi):
    climate_data=loadClimate(relative_path,date,rcp_scenario, ssp_scenario, tas_percentil,uhi) # Load data first
    year=int(date[0:4]) #get first year from the date string
    mean_summer_temperatures_all_years=np.empty((90,134))
    for year_value in range(year,year+5):
        mean_summer_temperatures_year=np.mean(climate_data['daily_climrisk_tas'].sel(time=slice(str(year_value)+'-4', str(year_value)+'-9')), axis=0)
        mean_summer_temperatures_all_years=np.dstack((mean_summer_temperatures_all_years,mean_summer_temperatures_year))  
        print(mean_summer_temperatures_all_years.shape)
    return mean_summer_temperatures_all_years