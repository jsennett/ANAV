import functools
from geopy.geocoders import Nominatim

import sys
sys.path.append('../')
from optimizer import graph_utils


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('search', __name__, url_prefix='/')

default_params = {
	'Destinationtext': '',
	'CurPostext': '',
	'length': 0,
	'route': [],
	'lat': 42.394021,
	'lon': -72.526652
}

@bp.route('/', methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		CurPos = request.form['CurPos']
		Destination = request.form['Destination']

		flatness_val = float(request.form['flatness_range'])/100
		bicycle_val = float(request.form['bicycle_range'])/100
		distance_val = float(request.form['distance_range'])/100

		motorway_val = float(request.form['motorway_range'])/100
		highway_val = float(request.form['highway_range'])/100
		residential_val = float(request.form['residential_range'])/100

		print("Flatness_val=",flatness_val)
		print("Bicycle_val=",bicycle_val)
		print("Distance_val=",distance_val)
		print("motorway_val=",motorway_val)
		print("highway_val=",highway_val)
		print("residential_val=",residential_val)

		error = None

		if CurPos is None or Destination is None:
			flash("Current position or destination cannot be blank.")
			return render_template('search.html', **default_params)

		if error is None:

			# Execute the search operation
			geolocator = Nominatim(user_agent="bikemap")
			CurPos_location = geolocator.geocode(CurPos)
			Destination_location = geolocator.geocode(Destination)

			print(CurPos_location, Destination_location)

			if Destination_location is None or CurPos_location is None:
				flash("Current position or destination was not found. Please provide a full, valid address.")
				return render_template('search.html', **default_params)

			print("Finding the shortest route from " )
			print(CurPos_location.latitude,CurPos_location.longitude)
			print("to")
			print(Destination_location.latitude, Destination_location.longitude)

			# Get Optimized route from the optimizer
			A = (CurPos_location.latitude, CurPos_location.longitude)
			B = (Destination_location.latitude, Destination_location.longitude)
			preferences = (flatness_val, bicycle_val, distance_val,
							motorway_val, highway_val, residential_val)

			route = graph_utils.optimize(A, B, preferences, debug=True)
			length = len(route)

			if length == 0:
				flash("No route found. Please try a different starting position or end destination.")
				return render_template('search.html', **default_params)
			else:
				return render_template('search.html',
										Destinationtext = Destination,
										CurPostext = CurPos,
										length = length,
										route = route,
										lat=CurPos_location.latitude,
										lon=CurPos_location.longitude)
		else:
			flash(error);
	return render_template('search.html', **default_params)
