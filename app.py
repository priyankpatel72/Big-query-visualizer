import os
from datetime import datetime
from flask import Flask
from flask import Flask, render_template, redirect, request, url_for, session

import pandas as pandas
import numpy as np 
import matplotlib.pyplot as plt 

from shapely.geometry import Point, Polygon
import geopandas as gpd
from geopandas import GeoDataFrame
import descartes

from google.cloud import bigquery
import googlemaps

PROJECT_ID = "big-query-database"
API_KEY = '********************************************************'
# client = bigquery.Client(projct = PROJECT_ID)

app = Flask(__name__, template_folder = 'template', static_url_path = '/src/')

@app.route("/")
@app.route("/index")
def loadHomePage():
	print("Loading Home Page")
	return render_template('index.js')


@app.route('/<path:path>', methods = ['GET'])
def send_file(path):
	strFile = path
	return app.send_static_file(strFile)
	app.use_x_sendfile()

@app.route('/getLocation', methods = ['POST', 'GET'])
def getLocation():
	user = request.form
	coords = []
	LOCATION = user['location']
	coords = getCoordinates(LOCATION)
	return render_template('map.html', label = coords)

def getCoordinates(LOCATION):
	gmaps = googlemaps.Client(key = API_KEY)
	coords = []
	geocode_result = gmaps.geocode(LOCATION)
	NORTH_EAST_LAT = geocode_result[0]['geometry']['bounds']['northeast']['lat']
	NORTH_EAST_LNG = geocode_result[0]['geometry']['bounds']['northeast']['lng']
	SOUTH_WEST_LAT = geocode_result[0]['geometry']['bounds']['southwest']['lat']
	SOUTH_WEST_LNG = geocode_result[0]['geometry']['bounds']['southwest']['lng']
	coords = [NORTH_EAST_LAT, NORTH_EAST_LNG, SOUTH_WEST_LAT, SOUTH_WEST_LNG]
	weatherStationsdf = getWeatherStationLocation(coords)
	return weatherStationsdf

def getWeatherStationLocation(coords):
	query1 = "SELECT id,name,state,latitude,longitude FROM `bigquery-public-data.ghcn_d.ghcnd_stations` WHERE latitude > "+str(coords[2])+" AND latitude < "+str(coords[0])+" AND longitude > "+str(coords[3])+" AND longitude < "+str(coords[1])+";"
	response = client.query(query1).to_dataframe()
	crs = {'init':'espg:4326'}
	weatherStation = [Point(xy) in xy in zip(response['longitude'], response['latitude'])]
	weatherStationPoints = gpd.GeoDataFrame(response, crs = crs, geometry = weatherStation)
	return weatherStationPoints


if __name__ == '__main__':
    ## start API
    app.run()
