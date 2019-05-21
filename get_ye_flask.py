#Import Libraries
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template

'''DB Setup'''

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#reflect the db into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#make references to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

#create a session
session = Session(engine)

#make an app instance
app = Flask(__name__)

#Use FLASK to create your routes.

#index
@app.route('/')
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/precipitation<br/>"
        f"- Prior year precipitation totals from Hawaii weather stations.<br/>"
        f"<br/>"
        f"/api/stations<br/>"
        f"- List of Hawaii weather station numbers and names.<br/>"
        f"<br/>"
        f"/api/temperature<br/>"
        f"- Prior year temperatures from all Hawaii weather stationss<br/>"
        f"<br/>"
        f"/api/start<br/>"
        f"- Provide the start date in YYYY-MM-DD format to get the Minimum, Maximum and Average Temperatures for all dates inclusive from the start date until the last date on the list, 2017-08-23.<br/>"
        f"<br/>"
        f"/api/start/end<br/>"
        f"- Provide both the the start date and the end date in YYYY-MM-DD format to get the Minimum, Maximum and Average Temperatures for dates between the start and end date, inclusive.<br/>"
    )

#########################################################################################
#precipitation
#    * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#    * Return the json representation of your dictionary.
@app.route('/api/precipitation/')
def precipitation():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    prcp_totals = []
    for result in prcp:
        prcp_dict = {}
        prcp_dict["date"] = prcp[0]
        prcp_dict["prcp"] = prcp[1]
        prcp_totals.append(prcp_dict)

    return jsonify(prcp_totals)

#########################################################################################

#stations
#   *Return a JSON list of stations from the dataset
@app.route('/api/stations/')
def stations():
    session = Session(engine)
    station_query = session.query(Station).all()
    stations = []
    for station in station_query:
        stations_dict = {}
        stations_dict["Station"] = station.station
        stations_dict["Station Name"] = station.name
        stations_dict["Latitude"] = station.latitude
        stations_dict["Longitude"] = station.longitude
        stations_dict["Elevation"] = station.elevation
        stations.append(stations_dict)

    return jsonify(stations)

#########################################################################################

#temperature
#   *Query for the dates and temperature observations from a year from the last data point.
#   *Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/temperature/')
def temperature():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temps_query = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    temperatures = []
    for temperature in temps_query:
        temps_dict = {}
        temps_dict["date"] = temps_query[0]
        temps_dict["tobs"] = temps_query[1]
        temperatures.append(temps_dict)

    return jsonify(temperatures)

#########################################################################################
# start and start/end
#   Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   *When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#   *Hint: You may want to look into how to create a defualt value for your route variable.
#   *When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/<start>/')
def start_date(start=None):
    """Fetch date whose starting date matches the path variable supplied by the user, or a 404 if not."""
    session = Session(engine)
    start_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    start_stats = []
    for start_min, start_max, start_avg in start_query:
        start_dict = {}
        start_dict["Minimum Temp"] = start_min
        start_dict["Maximum Temp"] = start_max
        start_dict["Average Temp"] = start_avg
        start_stats.append(start_dict)

    return jsonify(start_stats)

@app.route('/api/<start>/<end>/')
def end_date(start=None, end=None):
    """Fetch date whose starting date and ending matches the path variable supplied by the user, or a 404 if not."""

    session = Session(engine)
    end_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    end_stats = []
    for end_min, end_max, end_avg in end_query:
        end_dict = {}
        end_dict["Minimum Temp"] = end_min
        end_dict["Maximum Temp"] = end_max
        end_dict["Average Temp"] = end_avg
        end_stats.append(end_dict)

    return jsonify(end_stats)

#########################################################################################

#Debug and clearing my cache

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
