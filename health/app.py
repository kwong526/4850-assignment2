from time import strftime
import uuid
import connexion
from connexion import NoContent
import datetime
import requests
import json
import yaml
import logging, logging.config
from flask_cors import CORS, cross_origin
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from health import Health


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def create_table():
    """create the table if it doesn't exist"""
    conn = sqlite3.connect(app_config['datastore']['filename'])
    c = conn.cursor()
    c.execute('''
        CREATE TABLE if not exists health
        (id INTEGER PRIMARY KEY ASC, 
        receiver VARCHAR(10) NOT NULL,
        storage VARCHAR(10) NOT NULL,
        processing VARCHAR(10),
        audit VARCHAR(10),
        last_updated VARCHAR(100) NOT NULL)
        ''')

    conn.commit()
    conn.close()

def display_health_status():
    """get the stats from storage application"""
    session = DB_SESSION()
    time = datetime.datetime.now()
    readings = session.query(Health).order_by(Health.last_updated.desc()).first()
    
    if readings == None:
        ss = Health('Down','Down','Down','Down', time)
        session.add(ss)
        session.commit()
        readings = session.query(Health).order_by(Health.last_updated.desc()).first()
        result = readings.to_dict()
        session.close()
        return result, 201

    else:
        result = readings.to_dict()
        session.close()    
        return result, 201


def populate_db():
    """ store the result in sqlite """
    session = DB_SESSION()
    time = datetime.datetime.now()
    create_table()
    result = session.query(Health).order_by(Health.last_updated.desc()).first()
   

    if result == None:
        hc = Health('Down','Down','Down','Down', time)
    else:
        try:
            res_receiver = requests.get(app_config['eventstore']['receiver']+ "/" + "health" , timeout=5)
        
            # print(res_receiver.json())
            if res_receiver.status_code == 200:
                receiver = 'Running'
        except:
            receiver = 'Down'
        try:
            res_storage = requests.get(app_config['eventstore']['storage']+ "/" + "health", timeout=5)
            if res_storage.status_code == 200:
                storage = 'Running'
        except:
            storage = 'Down'
        
        try:
            res_processing = requests.get(app_config['eventstore']['processing']+ "/" + "health", timeout=5)
            if res_processing.status_code == 200:
                processing = 'Running'
        except:
            processing = 'Down'
        
        try:
            res_audit = requests.get(app_config['eventstore']['audit']+ "/" + "health", timeout=5)
            if res_audit.status_code == 200:
                audit = 'Running'
        except:
            audit = 'Down'
  
        hc = Health(
        receiver,
        storage,
        processing,
        audit,
        time
        )
        
        # session.add(bs)
    session.add(hc)
    session.commit()
    session.close()
    return NoContent, 201

def init_scheduler():
    """ initialize the scheduler to run periodically"""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_db,
                'interval',
                seconds=app_config['scheduler']['period_sec']
                )
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120)