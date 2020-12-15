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
from pathCORDEX import * # Import path to CORDEX data

def save(corrMatrix,relative_path,gcm,rcp,rp,rcm,version,date):
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
    data_path = relative_path + "/" + gcm + "/" + var + "/" + rcp + "/" + var + "_EUR-11_" + gcm + "_"+ rcp+ "_"+ rp+ "_"+rcm+"_"+ version+ "_day_"+ date + ".nc"
    try:
        data = xr.open_dataset(data_path)
        print("Successful load: "+ data_path)
    except Exception as e: 
        print(e)
        data=[]

    return data