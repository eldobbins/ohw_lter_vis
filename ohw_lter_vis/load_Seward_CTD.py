#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code is designed to ingest a CTD pair of data and header files from:
https://portal.aoos.org/old/gulf-of-alaska#metadata/e25fe1f2-1c98-44f6-856f-5d61c87c0384/project/files

Data are placed into a pandas dataframe and gieven a datetime column 
for future alignment with zooplankton data.

Created on Wed Aug 22 16:23:35 2018

@author: EDobbins
"""

import pandas as pd
import csv
import requests


def count_header_lines(url):
    """ Counts header lines in a CTD file.
    Seward Line CTD files have a variable number of header lines at the top of
    the file.  This function count the header rows by looking for the 'END' string
    that terminates it.
    
    Args:
        url : the URL of the CTD data file (string)
    Returns:
        the number of header lines that need to be skipped when reading (int)
    """
    
    nhdr=0
    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            nhdr+=1
            if row[0].find('END')>1:  # Warning: I've seen cases with "END" in station name
                #print(row[0])
                break
    return(nhdr)


def get_column_names(url):    # start the list of column headers
    """ Gets column names from the header.
    Seward Line CTD files have a section in the header lines that define
    what the columns are in the file.  This function parses those by
    looking for the strings that mark the section's beginning and end. What it 
    finds is broken into two parts: the SBE defined variable code, and a
    descriptive string that includes the units.
    
    TODO: There is a kludged section that shifts some of the variable names
     to what the notebooks in this package are expecting.  This should be 
     refined in the future.
    
    Args:
        url : the URL of the CTD data file (string)
    Returns:
        a tuple containing 2 lists of strings:
            the SBE variable names that came from the .cnv files
            the SBE variable descriptions that include units etc.
    """
    
    NAMES = False  # this will trigger at the beginning of variable names section
    varnames = []
    vartitles = []
    
    # with open(datafile, 'r') as csvfile:
    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=':')
        for row in cr:
            if NAMES and row[0][1] == '%':  # names section ends with row of %
                break
            if NAMES:
                index = row[0].replace('% ', '')   # the first column is the index
                varnames.append(row[1].strip())
                vartitles.append(row[-1].strip())
                if int(index) != len(varnames):    # if the index doesn't match number of variables
                    print('you gotta problem')
            if row[0].find('Data File Column Contents')>1: NAMES = True
    
    # before return it, make some variable names like they were before so 
    # notebooks don't break
    varnames = [v.replace('Consecutive Station Number', 'id') for v in varnames]
    varnames = [v.replace('prDM', 'pressure') for v in varnames]
    varnames = [v.replace('t090C', 'temperature') for v in varnames]
    varnames = [v.replace('sal00', 'salinity') for v in varnames]
    
    return (varnames, vartitles)


def load_data(url):
    """  Reads data from an online CSV into a pandas dataframe.  
    Note: the columns 
    are parsed out of the data file header.
    
    Args:
        url : the URL of the CTD data file (string)
    Returns:
        a pandas.DataFrame that is the data from the file
    """
    
    # There are 30 columns names that were originally hardcoded during OHW.
    # The notebooks still expect these names.
#    colnames = [ 'id', 'pressure', 'temperature', 'temperature2', 'conductivity','conductivity2', 
#           'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7',
#           'fluorescence', 'beam_trans', 'oxygen', 
#           'altimeter', 'latitude', 'longitude', 'density', 'density2',
#           'salinity', 'salinity2', 'nbin', 'flag']
    
    # Get some data from the header lines that are used as arguments to read 
    nhdr = count_header_lines(url)
    (colnames, vartitles) = get_column_names(url)

    return pd.read_table(url, skiprows=nhdr, names=colnames, delim_whitespace=True)


def load_header(url):
    """ Reads station information into a pandas dataframe.
    Read station information from an online CSV (called a header file) and put
    it into a pandas dataframe.  Note: the columns must be hardcoded, because 
    nothing is listed within the file.  Always seem to be the same.
    
    Args:
        url : the URL of the CTD header file (string)
    Returns:
        a pandas.DataFrame that is the station data from the file 
    """
    
    # define the column names
    hcolnames = [ 'id', 'station', 'date', 'latitude', 'longitude','waterdepth', 
           'filename', 'instrument', 'ship', 'cruise', 'junk1', 'PI', 'purpose',
           'agency', 'region', 'junk2']
    
    # read the data and set the index
    hdata = pd.read_csv(url, delimiter=',', names=hcolnames)
    hdata = hdata.set_index('id')
    return hdata


def make_CTD_dataframe():
    """ Returns CTD data from the Seward Line.
    Read data and station info from online CSV files and combines them into 
    to make a single pandas dataframes.
    
    TODO: this function only returns a single year because the URLs include 
     a hash that cannot be predicted.  Eventually, one could extend it to 
     other years by recording all the required URLs.
    
    Args:
        none
    Returns:
        a pandas.DataFrame that combines the CTD data and station information
    """

    # data file URLs were copied from links in the AOOS portal:
    # https://portal.aoos.org/old/gulf-of-alaska.php#metadata/e25fe1f2-1c98-44f6-856f-5d61c87c0384/project
    hdrurl = 'https://workspace.aoos.org/published/file/6be0d8f6-5ddc-4ad9-90d3-8a63d5d58752/TXS12.hdr'
    dataurl = 'https://workspace.aoos.org/published/file/62874c7d-d4ac-4d59-b349-cc402d872d7f/TXS12.ascii'

    # load the two separate files
    data= load_data(dataurl)
    hdata = load_header(hdrurl)

    # join these two together so that data are associated with positions
    df = pd.merge(data,hdata, on='id')
    df['time'] = pd.to_datetime(df['date'])
    df = df.drop(columns=['latitude_x','longitude_x'])
    df = df.rename(columns={'latitude_y':'latitude','longitude_y': 'longitude'})
    return df


def main():
    make_CTD_dataframe()


if __name__== "__main__":
    main()



