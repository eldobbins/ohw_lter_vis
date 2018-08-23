# -*- coding: utf-8 -*-
"""
This code is designed to ingest the zooplankton file from here:
    https://workspace.aoos.org/published/file/6c544f8c-6662-4298-bdcf-52029d113c61/Seward_ZooData_Calvet_%202012-2016_final.csv
and trim it, clean it, and place it into a pandas dataframe. I will also create
a datetime column for future alignment with environmental data.
"""

#import the necessary libraries
import pandas as pd
from datetime import datetime

def make_zooplankton_dataframe(year=None):
    
    """Will collect the CSV file, clean it, and fit it into a pandas DataFrame
       for use in further visualization.
       
       Input
       -----
           year = int (optional)    Limit the return dataframe to a single year
                                    Must be in the 2012 - 2016 timeframe
           
                      
       Returns
       -------
           m : pandas.DataFrame       The cleaned CSV file of zooplankton abundance
           
           
    """
       
    infilename='https://workspace.aoos.org/published/file/6c544f8c-6662-4298-bdcf-52029d113c61/Seward_ZooData_Calvet_2012-2016_final.csv'
    zooplankton_data = pd.read_csv(infilename, header=0, index_col=0)
    
    #trim off the excess columns that may appear due the CSV formatting
    keep_columns = zooplankton_data.columns[:32]
    keep_columns = keep_columns.drop('Date-Time')
    keep_columns
    zooplankton_data_trimmed = pd.DataFrame(zooplankton_data, columns=keep_columns)
    zooplankton_data_trimmed.rename(columns={'Latitude (degrees N)': 'latitude'})
    zooplankton_data_trimmed.rename(columns={'Longitude (degrees W)': 'longitude'})
    #create the datetime column for merging with environmental/other datasets
    zooplankton_data_trimmed['time'] = [datetime(
                                        x[1]['Year'], 
                                        x[1]['Month'], 
                                        x[1]['Day'], 
                                        int(x[1]['Time (hh:mm:ss AM/PM)'].split(':')[0]), 
                                        int(x[1]['Time (hh:mm:ss AM/PM)'].split(':')[1]),
                                        ) for x in zooplankton_data_trimmed.iterrows()]
    if year:
        if 2012 <= int(year) <= 2016:
            return zooplankton_data_trimmed.groupby('Year').get_group(int(year))
        else:
            print('That year is not included in the dataset')
            return None
    else:
        return zooplankton_data_trimmed
    

