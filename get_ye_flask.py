#dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template

'''DB Setup'''

engine = create_engine('sqlite:///hawaii.sqlite')

#reflect the db into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#make references to the tables
Station = Base.classes.station
Measurements = Base.classes.measurement

#create a session
session = Session(engine)

#make an app instance
app = Flask(__name__)

'''Define the Routes'''

#index
@app.route('/')
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/temperature<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )

#precipitation for the last 12 months
@app.route('/api/v1.0/precipitation/')
def precipitation():
    """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    session = Session(engine)
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#########################################################################################

#list of stations
@app.route('/api/v1.0/stations/')
def stations():
    session = Session(engine)
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

#########################################################################################
# the lastest date 8/23/2017 as such the last 12 month is from 8-24-2016 to 8-23-2017
YearBeg = dt.datetime(2016,8,23) #set one less date before the year beg date 8/24
YearEnd = dt.datetime(2017,8,24) #set one more date after the year end date 8/23

#temperature observations for the last 12 months
@app.route('/api/v1.0/temperature/')
def temperature():
    session = Session(engine)
    """Return a list of temperatures for prior year"""
    # Design a query to pull date and tobs values for previous year (last 12 months)
    result3 = session.query(Measurements.date, Measurements.tobs).\
    filter(Measurements.date > YearBeg).filter(Measurements.date < YearEnd).statement

    # Save data in dataframe and set "date" as index
    Templs = pd.read_sql_query(result3, session.bind)
    #Templs.set_index('date',inplace=True) may or may not need to set the index - optional

    # turn df to dict
    df3_as_json = Templs.to_dict(orient='split')
    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': df3_as_json})
#########################################################################################
@app.route('/api/1.0/<start>/')
def start(startdate):
    session = Session(engine)
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return (
            f"<a href=/welcome> Back to Main Page</a><br><br>"
            f"Please enter Start Date in YYYY-MM-DD format.<br>")
    one_yr = dt.timedelta(days=365)
    startdate = start_date-one_yr
    enddate =  dt.date(2017, 8, 23)
    tobs_calc = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    tobs_stats = list(np.ravel(tobs_calc))
    return jsonify(tobs_stats)

@app.route('/api/1.0/<start>/<end>/')
def end(startdate, enddate):

    session = Session(engine)
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return (
            f"<a href=/welcome> Back to Main Page</a><br><br>"
            f"Please enter Start Date in YYYY-MM-DD format.<br>")
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    one_yr = dt.timedelta(days=365)
    startdate = start_date-last_year
    enddate = end_date-last_year
    start_end_tobs = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    one_yr_start_end_tobs = list(np.ravel(start_end_tobs))
    return jsonify(one_yr_start_end_tobs)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)
