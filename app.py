# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Create your welcome endpoint with the several different routes
@app.route('/')
def welcome():
    
    return(
        f"Weclome to the Hawaiian Weather API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Available Routes with Customizable Input:<br/>"
        f"/api/v1.0/start/yyyy-mm-dd<br/>"
        f"/api/v1.0/start/yyyy-mm-dd/end/yyyy-mm-dd"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the dataset and collect the date from one year prior
    recent_date = dt.date(2017, 8, 23)
    one_year_ago = recent_date - dt.timedelta(days = 365)

    # Query the prcp 'data' and 'prcp' for the past 12 months from the Measurement table
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
                 filter(Measurement.date >= one_year_ago).all()

    # Close the session
    session.close()
    
    # Create dictionary with dates as keys and prcp as values
    prcp_data = []
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)
    
    # Return the JSON representation of dictionary
    return jsonify(prcp_data)

    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the 'id', 'station', and 'name' from the Station table
    results = session.query(Station.id,Station.station,Station.name).all()
    
    # Close the session
    session.close()
    
    # Create a list of dictionaries for station data
    station_data=[]
    for id,station,name in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_data.append(station_dict)
    
    # Return the JSON representation of list
    return jsonify(station_data)
    
    
@app.route('/api/v1.0/tobs')
def most_active():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the dataset and collect the date from one year prior
    recent_date = dt.date(2017, 8, 23)
    one_year_ago = recent_date - dt.timedelta(days = 365)
    
    # Query the dates and temperatures of the most-active station for the previous year
    tobs_query = session.query(Measurement.date, Measurement.tobs).\
        filter_by(station = "USC00519281").\
        filter(Measurement.date >= one_year_ago).all()
    
    # Close the session
    session.close()
    
    # Create a list of dictionaries for temperature data
    tobs_data = []
    for date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_data.append(tobs_dict) 
    
    # Return the JSON representation of list
    return jsonify(tobs_data)


@app.route('/api/v1.0/start/<start>')
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Set up the function list for query
    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)
    ]
    
    # Query the data greaater than or equal to the start date
    start_filter = session.query(*sel).filter(Measurement.date >= start).all()
    
    start_list = [
        {"TMIN": start_filter[0][0]},
        {"TAVG": start_filter[0][1]},
        {"TMAX": start_filter[0][2]}
    ]
    
    if start <= '2017-08-23':
        return jsonify(start_list)
    else:
        return jsonify("Error: start date past time horizon, please enter a date before 2017-08-23'")
    
    # Close the session
    session.close()

    
@app.route('/api/v1.0/start/<start>/end/<end>')
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Set up the function list for query
    sel = [func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)
    ]
    
    # Query the data between the start and end dates
    start_end_filter = session.query(*sel).\
        filter(Measurement.date.between(start,end)).all()
    
    start_end_list = [
        {"TMIN": start_end_filter[0][0]},
        {"TAVG": start_end_filter[0][1]},
        {"TMAX": start_end_filter[0][2]}
    ]
    
    if (start <= '2017-08-23') and (end >='2010-01-01') :
        return jsonify(start_end_list)
    else:
        return jsonify("Error: start and end date not within time horzion, please enter a start and end date between 2010-01-01 : 2017-08-23")
    
    # Close the session
    session.close()
    
    
if __name__ == '__main__':
    app.run(debug=True)
