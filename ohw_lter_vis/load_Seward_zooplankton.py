# -*- coding: utf-8 -*-
"""
This code is designed to ingest a zooplankton file from:
https://portal.aoos.org/old/gulf-of-alaska#metadata/e25fe1f2-1c98-44f6-856f-5d61c87c0384/project/files

Data are trimmed to the correct date range, cleaned, placed into a pandas 
dataframe, and given a datetime column is also created for future alignment 
with CTD data.

Created on Wed Aug 22 16:23:35 2018

"""

#import the necessary libraries
import pandas as pd
from datetime import datetime

def make_zooplankton_dataframe(year=None):
    """ Makes a pandas dataframe from zooplankton data.
    Will collect the CSV file from a URL, clean it, and put it in a pandas 
    DataFrame for use in further visualization.
       
    Args:
        year : int (optional) Limit the return dataframe to a single year
               Must be in the 2012 - 2016 timeframe
    Returns:
        a pandas.DataFrame that is the cleaned zooplankton abundance
    """
       
    # read the data
    dataurl = 'https://workspace.aoos.org/published/file/6c544f8c-6662-4298-bdcf-52029d113c61/Seward_ZooData_Calvet_2012-2016_final.csv'
    zooplankton_data = pd.read_csv(dataurl, header=0, index_col=0, 
                                   encoding='latin_1')
    
    # trim off the excess columns that may appear due the CSV formatting
    keep_columns = zooplankton_data.columns[:32]
    keep_columns = keep_columns.drop('Date-Time')
    zooplankton_data_trimmed = pd.DataFrame(zooplankton_data, columns=keep_columns)
    
    # rename variables to match those in CTD file
    zooplankton_data_trimmed.rename(columns={'Latitude (degrees N)': 'latitude'}, inplace=True)
    zooplankton_data_trimmed.rename(columns={'Longitude (degrees W)': 'longitude'}, inplace=True)
    
    # create the datetime column for merging with environmental/other datasets
    zooplankton_data_trimmed['time'] = [datetime(
                                        x[1]['Year'], 
                                        x[1]['Month'], 
                                        x[1]['Day'], 
                                        int(x[1]['Time (hh:mm:ss AM/PM)'].split(':')[0]), 
                                        int(x[1]['Time (hh:mm:ss AM/PM)'].split(':')[1]),
                                        ) for x in zooplankton_data_trimmed.iterrows()]
    
    # trim by year
    if year:
        if 2012 <= int(year) <= 2016:
            zooplankton_data_trimmed = zooplankton_data_trimmed.groupby('Year').get_group(int(year))
        else:
            print('That year is not included in the dataset')
            zooplankton_data_trimmed = None
    
    return zooplankton_data_trimmed
    

