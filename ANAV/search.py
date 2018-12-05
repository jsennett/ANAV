import functools
from geopy.geocoders import Nominatim

import sys
sys.path.append('../')
from optimizer import graph_utils


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('search', __name__, static_folder="../", url_prefix='/search')

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


		#f = request.form['flatness_range']
		error = None

		if CurPos is None:
			error = 'Current Pisition is required.'
		elif Destination is None:
			error = 'Destination is required.'
		else:
			error = None

		if error is None:
			# Execute the search operation
			#print('CurPos = ' + CurPos )
			#print('Destination =' + Destination )
			geolocator = Nominatim(user_agent="bikemap")
			CurPos_location = geolocator.geocode(CurPos)
			Destination_location = geolocator.geocode(Destination)

			if Destination_location is None or CurPos_location is None:
				return render_template('routenotfound.html')


			print("Finding the shortest route from " )
			print(CurPos_location.latitude,CurPos_location.longitude)
			print("to")
			print(Destination_location.latitude, Destination_location.longitude)

			# Get Optimized route from the optimizer
			#route = graph_utils.optimize(CurPos_location.latitude,CurPos_location.longitude,
			#					 Destination_location.latitude, Destination_location.longitude)


			route = get_route(CurPos_location.latitude,CurPos_location.longitude, Destination_location.latitude, Destination_location.longitude)
			
			length = len(route);
			
			return render_template('search.html',Destinationtext = Destination, CurPostext = CurPos, length = length, route = route)

		flash(error);
	return render_template('search.html')


def get_route(CurPos_latitude, CurPos_longtitude, Des_latitude, Des_longtitude):
	#check databese
	route = [[CurPos_latitude, CurPos_longtitude,50],[37.772,-122.214,40],[-27.467,153.027,10], [Des_latitude, Des_longtitude,80]]
	return route
