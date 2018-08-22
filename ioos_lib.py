# !/usr/env/python

'''
This script is code largely generated from the Ocean Hackweek Tutorials on retrieving OOI data, with some additions and formatting done by the script authors to use the code more functionally in an API for data retrieval.
'''

# helpful libraries and packages for this library
import numpy as np 
import pandas as pd 
import geopandas as gpd 
import matplotlib.pyplot as plt 
import matplotlib 
import folium
import shapely.geometry as shpgeom 
import cartopy.crs as ccrs
from cartopy.io.img_tiles import StamenTerrain
from owslib import fes
from datetime import datetime, timedelta
from ioos_tools.ioos import fes_date_filter, get_csw_records
from owslib.csw import CatalogueServiceWeb
from geolinks import sniff_link
import re
from itertools import cycle

class DataScraper():
    '''
    An object with helper functions for accessing and querying data from the IOOS site
    '''

    def __init__(self, roi, start, stop, target=None):
        self.roi = roi
        self.min_lon, self.max_lon, self.min_lat, self.max_lat = roi[0], roi[1], roi[2], roi[3]
        self.start = start
        self.stop = stop
        self.target = target

    def draw_roi(self):
        '''
        Helper function for seeing the region of interest being queried
        '''

        fig, ax = plt.subplots(1, figsize=(8,8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent((self.min_lon-1, self.max_lon+1, self.min_lat-1, self.max_lat+1))
        ax.add_image(StamenTerrain(), 8)
        ax.coastlines(resolution='10m')
        ax.gridlines(draw_labels=True, color='0.8')

        query_bbox_shp = shpgeom.box(self.min_lon, self.min_lat, self.max_lon, self.max_lat)
        query_bbox_gs = gpd.GeoSeries(query_bbox_shp)

        query_bbox_gs.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=3)

    def make_bbox(self):
        crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'
        self.bbox_crs = fes.BBox(self.roi, crs=crs)

    def make_fes_filter(self):
        begin, end = fes_date_filter(self.start, self.stop)
        kw = dict(wildCard='*',escapeChar='\\',singleChar='?',propertyname='apiso:AnyText')
        or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw) for val in self.target])
        self.filter_list = [fes.And([self.bbox_crs, begin, end, or_filt, fes.Not([fes.PropertyIsLike(literal='*cdip',**kw)]),
                                fes.Not([fes.PropertyIsLike(literal='*grib*', **kw)])])]

    def get_records(self):
        endpoint = 'https://data.ioos.us/csw'
        self.csw = CatalogueServiceWeb(endpoint, timeout=60)
        get_csw_records(self.csw, self.filter_list, pagesize=10, maxrecords=1000)
        self.records= '\n'.join(self.csw.records.keys())
        print('Found {} records.\n'.format(len(self.csw.records.keys())))

    def select_record(self):
        #print the unique record list
        #allow user to select the instrument(s) of interest
        self.assets = []
        for k,v in list(self.csw.records.items()):
            print(u'[{}]\n {}'.format(v.title, k))
            self.assets.append(self.csw.records[v.title])

    def create_database(self):
        df = []
        for k,v in self.csw.records.items():
            df.append(pd.DataFrame(v.references))

        df = pd.concat(df, ignore_index=True)
        df['geolink'] = [sniff_link(url) for url in df['url']]
        self.df = df

    def get_observations(self):
        sos_urls = [fix_series(url, self.start, self.stop) for url in self.df.loc[self.df['geolink'] == 'OGC:SOS', 'url'] if 'GetObservation' in url and 'text/csv' in url and self.target[0] in url]
        self.observations = []
        for url in sos_urls:
            temp = pd.read_csv(url)
            print(temp.columns)
            try:
                self.observations.append(pd.read_csv(url, index_col='date_time', parse_dates=True))
            except:
                pass

    def plot_observations(self):
        with matplotlib.style.context('seaborn-notebook'):
            fig, ax = plt.subplots(figsize=(11, 2.75))
            colors = mpl_palette(plt.cm.Set2, n_colors=len(self.observations))
            for k, series in enumerate(self.observations):
                if k < 5:
                    station_name = series['station_id'].iloc[0].split(':')[-1]
                    ax.plot(series.index, series['sea_water_temperature (C)'], label=station_name, color=colors[k])
            leg = ax.legend(loc='upper center', ncol=10)

        # hours = matplotlib.dates.DateFormatter('%H:%M')
        # ax.xaxis.set_major_formatter(hours)

        # days = matplotlib.dates.DateFormatter('\n\n%Y-%m-%d')
        # ax.xaxis.set_minor_formatter(days)
        # ax.xaxis.set_minor_locator(matplotlib.ticker.FixedLocator([matplotlib.dates.date2num(self.start)]))


def fix_series(url, start, stop):
    url_split = re.split('[&?]', url)
    new_url = []
    for line in url_split:
        if line.startswith('eventTime='):
            line = f'eventTime={start:%Y-%m-%dT%H:%m:00}/{stop:%Y-%m-%dT%H:%m:00}'
        new_url.append(line)

    return "{}?{}".format(new_url[0], '&'.join(new_url[1:]))

def mpl_palette(cmap, n_colors=6):
    brewer_qual_pals = {"Accent": 8, "Dark2": 8, "Paired": 12,
                        "Pastel1": 9, "Pastel2": 8,
                        "Set1": 9, "Set2": 8, "Set3": 12}

    if cmap.name in brewer_qual_pals:
        bins = np.linspace(0, 1, brewer_qual_pals[cmap.name])[:n_colors]
    else:
        bins = np.linspace(0, 1, n_colors + 2)[1:-1]
    palette = list(map(tuple, cmap(bins)[:, :3]))

    pal_cycle = cycle(palette)
    palette = [next(pal_cycle) for _ in range(n_colors)]
    
    return palette

if __name__ == '__main__':
    # ds = DataScraper([-127, -123.75, 43, 48])
    days = 5
    now_datetime_utc = datetime.utcnow()
    start = now_datetime_utc - timedelta(days=days)
    stop = now_datetime_utc

    ds = DataScraper([-72, -69, 40, 45], start, stop, ['sea_water_temperature', 'sea_surface_temperature'])
    # ds.draw_roi()
    ds.make_bbox()
    ds.make_fes_filter()
    ds.get_records()
    ds.create_database()
    ds.get_observations()
    ds.plot_observations()
    plt.show()


