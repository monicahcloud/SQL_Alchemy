import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Base.classes.keys()
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
#Home page.
#List all routes that are available.
def welcome():
    print("Server received request for 'Home' page...")
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.o/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
    )
        
@app.route("/api/v1.0/precipitation")
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
def precipitation():
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0] 
    prev_year = (dt.datetime.strptime(last_date , '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>=prev_year).all()
    results
    prcp_list = []
    for date, prcp in results:
        prcp_list.append({date:prcp})

    prcp_list
    session.close()
    return jsonify(prcp_list)
    
@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    stations_list = list(np.ravel(results))
    session.close()
    return jsonify(stations_list)   
    
@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0] 
    prev_year = (dt.datetime.strptime(last_date , '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    results = session.query(measurement.tobs).filter(measurement.station== 'USC00519281')\
        .filter(measurement.date >= prev_year).all()
    temp_list = list(np.ravel(results))    
    session.close()
    return jsonify(temp_list)     


@app.route("/api/v1.0/<start>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

def start_temp(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs),\
              func.avg(measurement.tobs)\
              .filter(measurement.date >= start)).all()
    start_list = list(np.ravel(results))
    session.close()
    return jsonify(start_list)  

@app.route("/api/v1.0/<start>/<end>")
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.    
def end_temp(start = None, end= None):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs),\
        func.avg(measurement.tobs).filter(measurement.date >= start)\
        .filter(measurement.date <= end)).all()
    end_list = list(np.ravel(results))
    return jsonify(end_list)
    
if __name__ == '__main__':
    app.run(debug=True)
