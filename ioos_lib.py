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

class DataScraper():
	'''
	An object with helper functions for accessing and querying data from the IOOS site
	'''

	def __init__(self, roi):
		self.roi = roi
		self.min_lon, self.max_lon, self.min_lat, self.max_lat = roi[0], roi[1], roi[2], roi[3]

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
		kw = dict(wildCard='*',escapeChar='\\',singleChar='?',propertyname='apiso:AnyText')
		self.filter_list = [fes.And([self.bbox_crs, fes.Not([fes.PropertyIsLike(literal='*cdip',**kw)]),
								fes.Not([fes.PropertyIsLike(literal='*grib*', **kw)])])]

	def get_records(self):
		endpoint = 'https://data.ioos.us/csw'
		csw = CatalogueServiceWeb(endpoint, timeout=60)
		get_csw_records(csw, self.filter_list, pagesize=10, maxrecords=1000)
		self.records= '\n'.join(csw.records.keys())
		print('Found {} records.\n'.format(len(csw.records.keys())))


if __name__ == '__main__':
	# ds = DataScraper([-127, -123.75, 43, 48])
	ds = DataScraper([-72, -69, 40, 45])
	# ds.draw_roi()
	ds.make_bbox()
	ds.make_fes_filter()
	ds.get_records()
	plt.show()


