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
import xarray as xr
from pathCORDEX import * # Import path to CORDEX data
     
def corr2D(tas,hurs):
    """
    Computes the correlation between temperature (tas) and relative humidity (hurs) for a 2-D grid.
    Axis specifies the time dimension. Returns a 2-D matrix of correlation values for every cell.
    """
    corrMatrix=np.zeros((90,134))
    index=0
    for lat in range(90):
        for lon in range(134):
            corrMatrix[lat,lon]=np.corrcoef(tas['tas'][:,lat,lon],hurs['hurs'][:,lat,lon])[1,0]
            index=index+1
            #print('Completed: ' + str(round(index*100/12060,2)) +'%')
    return corrMatrix