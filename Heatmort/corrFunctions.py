"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Contains functions for preliminary statistical analysis (eg. correlations) of the CORDEX dataset.
"""

import netCDF4 as nc
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

             
def corr2D(tas,hurs,relative_path,gcm,rcp,rp,version,date):
    """
    Computes the correlation between temperature (tas) and relative humidity (hurs) for a 2-D grid.
    Axis specifies the time dimension. Returns a 2-D matrix of correlation values for every cell.
    """
    corrMatrix=np.zeros((90,134))
    for lat in range(90):
        for lon in range(134):
            corrMatrix[lat,lon]=np.corrcoef(tas['tas'][:,lat,lon],hurs['hurs'][:,lat,lon])[1,0]
    np.save(relative_path + "corrMatrix_EUR-11_"+ gcm + "_"+ rcp+ "_"+ rp+ "_SMHI-RCA4_"+ version+ "_day_"+ date + ".out",corrMatrix)


def load(relative_path,gcm,rcp,rp,version,date):
    """
    This function loads the tas and hurs data from CORDEX for a given
    1. GCM
    2. RCP scenario
    3. RP
    4. Version
    5. 5-year interval (between 2006 - 2100)
    """
    tas_path = relative_path + "/" + gcm + "/tas/" + rcp + "/" + "tas_EUR-11_"+ gcm + "_"+ rcp+ "_"+ rp+ "_SMHI-RCA4_"+ version+ "_day_"+ date + ".nc"
    hurs_path = relative_path + "/" + gcm + "/hurs/" + rcp + "/" + "hurs_EUR-11_" + gcm + "_" + rcp+ "_"+ rp + "_SMHI-RCA4_"+ version+ "_day_"+ date + ".nc"
    try:
        tas = xr.open_dataset(tas_path)
        try:
            hurs = xr.open_dataset(hurs_path)
        except:
            print("Can't load hurs: " + hurs_path) 
            tas=[]
            hurs=[]
    except:
        print("Can't load tmp: "+ tas_path)
        tas=[]
        hurs=[]

    return tas, hurs