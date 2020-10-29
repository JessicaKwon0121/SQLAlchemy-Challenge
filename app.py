from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>" 
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"       
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= year_ago).all()

    all_tobs = []
    for tobs in results:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats():

    sel = [func.min(Measurement.tobs), func.max(
           Measurement.tobs), func.avg(Measurement.tobs)]
    date_stats = session.query(Measurement.date)
    all_date = []
    for start, end in date_stats:
        date_dict = {}
        date_dict["date"] = date
        all_date.append(date_dict)
    
    if not end:
       results = session.query(*sel).\
                       filter(Measurement.date >= start).all()
       temp = list(np.ravel(results))
       return jsonify(temp)

    results = session.query(*sel).\
                    filter(Measurement.date > start).\
                    filter(Measurement.date < end).all()
        
    temp = list(np.ravel(results))
    return jsonify(temp)


if __name__ == '__main__':
    app.run(debug=True)