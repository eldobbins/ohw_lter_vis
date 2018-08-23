#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 16:23:35 2018

@author: EDobbins
"""

import pandas as pd
import csv
import requests


def count_header_lines(datafile):
    '''
    These funky CTD files have a variable number of header lines at the top of
    the file.  This function count the header rows by looking for the 'END' string
    that terminates it.
    
    :param datafile: the URL of the CTD data file (string)
    :returns nhdr: the number of header lines that need to be skipped when reading (int)
    '''
    
    nhdr=0
    with requests.Session() as s:
        download = s.get(datafile)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            nhdr+=1
            if row[0].find('END')>1:  # Warning: I've seen cases with "END" in station name
                #print(row[0])
                break
    return(nhdr)


def load_data(datafile):
    '''
    Read data from an online CSV into a pandas dataframe.  Note: the columns 
    are hardcoded, because they are listed as separate lines in the header, but
    they change from year to year. They should be parsed out to make it more 
    flexible
    
    :param datafile: the URL of the CTD data file (string)
    :returns data: the data from the file (Pandas DataFrame)
    '''
    # there are 30 columns whose names should be generated from the header. hardcode for now. 
    colnames = [ 'id', 'pressure', 'temperature', 'temperature2', 'conductivity','conductivity2', 
           'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7',
           'fluorescence', 'beam_trans', 'oxygen', 
           'altimeter', 'latitude', 'longitude', 'density', 'density2',
           'salinity', 'salinity2', 'nbin', 'flag']
    nhdr = count_header_lines(datafile)
    data = pd.read_table(datafile, skiprows=nhdr, names=colnames, delim_whitespace=True)
    return data


def load_header(hdrfile):
    '''
    Read station information from an online CSV (called a header file) and put
    it into a pandas dataframe.  Note: the columns must be hardcoded, because 
    nothing is listed within the file.  Always seem to be the same.
    
    :param hdrfile: the URL of the CTD header file (string)
    :returns hdata: the data from the file (Pandas DataFrame)
    '''
    hcolnames = [ 'id', 'station', 'date', 'latitude', 'longitude','waterdepth', 
           'filename', 'instrument', 'ship', 'cruise', 'junk1', 'PI', 'purpose',
           'agency', 'region', 'junk2']
    hdata = pd.read_csv(hdrfile, delimiter=',', names=hcolnames)
    hdata = hdata.set_index('id')
    return hdata


def make_CTD_dataframe():
    '''
    Read data and station info from online CSV files into a pandas dataframes
    and then combine them to make a single file.
    
    :returns df: the CTD data and station information (Pandas DataFrame)
    '''

    # data file names gotten by navigating via aoos portal to files, then copy link
    # still good?
    hdrfile = 'https://workspace.aoos.org/published/file/6be0d8f6-5ddc-4ad9-90d3-8a63d5d58752/TXS12.hdr'
    datafile = 'https://workspace.aoos.org/published/file/62874c7d-d4ac-4d59-b349-cc402d872d7f/TXS12.ascii'

    # load the two separate files
    data= load_data(datafile)
    hdata = load_header(hdrfile)

    # join these two together so that data are associated with positions
    df = pd.merge(data,hdata, on='id')
    df['time'] = pd.to_datetime(df['date'])
    df = df.drop(columns=['latitude_x','longitude_x'])
    df = df.rename(columns={'latitude_y':'latitude','longitude_y': 'longitude'})
    return df




