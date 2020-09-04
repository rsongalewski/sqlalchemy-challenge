import datetime as dt
from datetime import datetime, timedelta
import numpy as np

import pandas as pd 


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
 
#################################################
# Home Page
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    session = Session(engine)
    return (
        f"Hawaii Precipitation and Weather Data<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipiation from 2016-08-23 to 2017-08-23:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"A list of all the weather stations in Hawaii:<br/>" 
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"The Temperature Observations from 2016-08-23 to 2017-08-23:<br/>" 
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Type in a single date (i.e., 2015-01-01) to see the min, max and avg temperature since that date:<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"Type in a date range (i.e., 2015-01-01/2015-01-10) to see the min, max and avg temperature for that range:<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
    )
#########################################################################
# Precipitation by Date over a Year
#########################################################################
most_recent_date = dt.date(2017, 8, 23)
start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp, Station.name).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.station == Station.station).\
        order_by(Measurement.date).all()

    precipitation_data = []
    for prcp_data in results:
        prcp_data_dict = {
            'Name': prcp_data.name,
            'Date' : prcp_data.date,
            "Precipitation" : prcp_data.prcp
        }
        precipitation_data.append(prcp_data_dict)
        

    return jsonify(precipitation_data)

#########################################################################
# Station Names
#########################################################################
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station).all()
    # Create a dictionary from the row data and append to a list of all_stations.
    all_stations = []
    for stations in results:
        stations_dict = {
            "Station": stations.station,
            "Station Name": stations.name,
            "Latitude": stations.latitude,
            "Longitude": stations.longitude,
            "Elevation": stations.elevation
        }
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

#########################################################################
# Temperature Observations over a Year
#########################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query all the stations and for the given date.
    session = Session(engine)
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= start_date).\
                    filter(Measurement.station == Station.station).\
                    order_by(Measurement.date).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in results:
        tobs_data_dict = {
            "Name": tobs_data.name,
            "Date": tobs_data.date,
            "Temperature": tobs_data.tobs
        }
        temp_data.append(tobs_data_dict)

    return jsonify(temp_data)

#########################################################################
# Start Date Only
#########################################################################
@app.route("/api/v1.0/<start>")
def start(start=None):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start, most_recent_date)).all()
    temp_data = []
    for Tmin, Tavg, Tmax in results:
        temps = {
            'Minimum Temp': Tmin,
            'Average Temp': Tavg,
            'Maximum Temp': Tmax
        }
        temp_data.append(temps)

    return jsonify(temp_data)

#########################################################################
# Start & End Date
#########################################################################
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()

    temp_data = []
    for Tmin, Tavg, Tmax in results:
        temps = {
            'Minimum Temp': Tmin,
            'Average Temp': Tavg,
            'Maximum Temp': Tmax
        }
        temp_data.append(temps)

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)