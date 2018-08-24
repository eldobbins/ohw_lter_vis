import numpy as np
import pandas as pd
#from .due import due, Doi
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt


#__all__ = ["Model", "Fit", "opt_err_func", "transform_data", "cumgauss"]


# Use duecredit (duecredit.org) to provide a citation to relevant work to
# be cited. This does nothing, unless the user has duecredit installed,
# And calls this with duecredit (as in `python -m duecredit script.py`):
#due.cite(Doi("10.1167/13.9.30"),
#         description="Example project created during OceanHackWeek2018",
#         tags=["reference-implementation"],
#         path='ohw_lter_vis')


def make_map(projection=ccrs.PlateCarree(), figsize=(5, 5)):
    """
    Function that makes a basic map.

    Parameters
    ----------
    projection : map projection 

    Returns
    -------
    fig : matplotlib figure handle
    
    ax : matplotlib axis handle
    
    Note: From Filipe Fernandes's Geospatial and Mapping Tools tutorial
    OceanHackWeek 2018
    """
    fig, ax = plt.subplots(
        figsize=figsize,
        subplot_kw={'projection': projection})
    return fig, ax


def map_ngalter():
    """
    Function that makes a basic map of the NGA (Northern Gulf of Alaska) LTER
    study area.
  
    Note: Now is hardcoded for a study area, but maybe should be more flexible
    """
    fig, ax = make_map(projection=ccrs.LambertConformal(), figsize=(10, 10))

    ax.set_global()
    ax.coastlines(resolution='10m', color='k')
    ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='0.75')
    ax.set_extent([-154, -142, 58.5, 61.], ccrs.Geodetic())
    return fig, ax


def map_stations_data(ax ,df, colorby='temperature', colormap='viridis'):
    """
    Function that adds markers colored by a variable to locations on a map.

    Parameters
    ----------
    df : a Pandas DataFrame that must include the columns 'latitude', 
        'longitude', and the colorby variable
        
    colorby : string representing the DataFrame column to use as the color 
        scale for the markers
        
    colormap : string of colormap name

    Returns
    -------
    h : matplotlib handle
    
    ax : the matplotlib axis handle with the new markers added
    
    """

    h = ax.scatter(
        df['longitude'], df['latitude'],
        transform=ccrs.Geodetic(), s=200, c=df[colorby],
        edgecolors='blue', cmap=colormap,
        vmin=df[colorby].min(), vmax=df[colorby].max());
    return h, ax


    