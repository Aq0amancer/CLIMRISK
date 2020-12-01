"""
--------------------------------
CLIMRISK Model. Heatmort module.
--------------------------------
Main document to run anaylsis.
"""

import pandas
import netCDF4
from corrFunctions import load,corr2D # Import functions for correlation
from pathCORDEX import * # Import path to CORDEX data
from multiprocessing import Pool

rcps = ["rcp26", "rcp45", "rcp85"]
gcms = ["MPI-M-MPI-ESM-LR","CNRM-CERFACS-CNRM-CM5","ICHEC-EC-EARTH","IPSL-IPSL-CM5A-MR","MPI-M-MPI-ESM-LR","NCC-NorESM1-M","MOHC-HadGEM2-ES"]
rps = ["r12i1p1", "r1i1p1"]
versions = ["v1", "v1a"]

most_dates = [
    "20060101-20101231",
    "20110101-20151231",
    "20160101-20201231",
    "20210101-20251231",
    "20260101-20301231",
    "20310101-20351231",
    "20360101-20401231",
    "20410101-20451231",
    "20460101-20501231",
    "20510101-20551231",
    "20560101-20601231",
    "20610101-20651231",
    "20660101-20701231",
    "20710101-20751231",
    "20760101-20801231",
    "20810101-20851231",
    "20860101-20901231",
    "20910101-20951231",
    "20960101-21001231",
]
mohc_dates = [
    "20060101-20101230",
    "20110101-20151230",
    "20160101-20201230",
    "20210101-20251230",
    "20260101-20301230",
    "20300101-20351230",
    "20360101-20401230",
    "20410101-20451230",
    "20460101-20501230",
    "20510101-20551230",
    "20560101-20601230",
    "20610101-20651230",
    "20660101-20701230",
    "20710101-20751230",
    "20760101-20801230",
    "20810101-20851230",
    "20860101-20901230",
    "20910101-20951230",
    "20960101-20991230"]

def run(CORDEX_path,gcm,rcp,rp,version,date):
    [tas,hurs]=load(CORDEX_path,gcm,rcp,rp,version,date) # Load the tas and hurs data
    if any(tas): # Is the model name correct?
        corr2D(tas,hurs,CORDEX_path + '/corrMatrix/',gcm,rcp,rp,version,date) # Calculate the correlation matrix


if __name__=='__main__':
    pool = Pool(4) #use all available cores, otherwise specify the number you want as an argument
    for gcm in gcms:
        for rcp in rcps:
            for rp in rps:
                for version in versions:
                    if gcm=='MOHC-HadGEM2-ES': # MohC has a different labelling for the dates
                        dates=mohc_dates
                    else:
                        dates=most_dates
                    for date in dates:
                        pool.apply_async(run, args=(CORDEX_path,gcm,rcp,rp,version,date,))
    pool.close()
    pool.join()





