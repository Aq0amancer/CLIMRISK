"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Main document to run anaylsis.
"""

import pandas
import netCDF4
import parameters # import all parameters for CORDEX data
import corrFunctions # Import functions for correlation
import pathCORDEX # Import path to CORDEX data

for gcm in gcms:
    for rcp in rcps:
        for rp in rps:
            for version in versions:
                if gcm=='MOHC-HadGEM2-ES': # MohC has a different labelling for the dates
                    dates=mohc_dates
                else:
                    dates=dates
                for date in dates:
                    [tas,hurs]=load(CORDEX_path,gcm,rcp,rp,version,date) # Load the tas and hurs data
                    if any(tas): # Is the model name correct?
                        corr2D(tas,hurs,CORDEX_path + '/corrMatrix/',gcm,rcp,rp,version,date): # Calculate the correlation matrix
                        print('Completed corrMatrix for: ' + gcm + '-' + rcp + '-' + rp + '-' + version + '-' + date) # Print info



