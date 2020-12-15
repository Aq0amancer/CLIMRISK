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

for gcm in gcms:
    for rcp in rcps:
        for rp in rps:
            for rcm in rcms:
                for version in versions:
                    if gcm=='MOHC-HadGEM2-ES': # MohC has a different labelling for the dates
                        dates=mohc_dates
                    else:
                        dates=most_dates
                    for date in dates:
                        tas=load(relative_path,var,gcm,rcp,rp,rcm,version,date)
                        hurs=load(relative_path,var,gcm,rcp,rp,rcm,version,date)