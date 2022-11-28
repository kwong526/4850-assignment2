from sqlite3 import  connect
import requests
import connexion
from connexion import NoContent
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stats import Stats
from base import Base

import yaml, logging, logging.config
import datetime
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

from flask_cors import CORS, cross_origin

import os

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


def get_health_check():
    """return 200 status if its running"""
    return 200

def create_table():
    """create the table if it doesn't exist"""
    conn = sqlite3.connect(app_config['datastore']['filename'])
    c = conn.cursor()
    c.execute('''
        CREATE TABLE if not exists stats
        (id INTEGER PRIMARY KEY ASC, 
        num_buy_readings INTEGER NOT NULL,
        num_price_readings INTEGER NOT NULL,
        max_buy_readings INTEGER,
        max_price_readings INTEGER,
        min_buy_readings INTEGER,
        min_price_readings INTEGER,
        last_updated VARCHAR(100) NOT NULL)
        ''')

    conn.commit()
    conn.close()

def get_stats():
    """get the stats from storage application"""
    session = DB_SESSION()
    time = datetime.datetime.now()
    readings = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    
    if readings == None:
        ss = Stats(5,6,100, 200, 10,10, time)
        session.add(ss)
        session.commit()
        session.close()
        return None

    else:
        result = readings.to_dict()
        session.close()    
        return result, 201

def populate_stats():
    """ periodically update stats """
    session = DB_SESSION()
    time = datetime.datetime.now()
    create_table()
    result = session.query(Stats).order_by(Stats.last_updated.desc()).first()
   

    if result == None:
        Stats(5,6,100, 200, 10,10, time)
  
        
    else:
        last_updated = result.last_updated
        last_updated_format = str(last_updated.strftime("%Y-%m-%dT%H:%M:%SZ"))
        current_time_format = str(time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        res_buy = requests.get(
            app_config['eventstore']['url'] + "/" + "buy" + "?start_timestamp=" + last_updated_format + "&end_timestamp=" + current_time_format
            )
        buy_data = res_buy.json()
        buy_price = []
        
        
        for item in buy_data:
            print(item['price'])
            buy_price.append(float(item['price']))
        
        res_price = requests.get(
            app_config['eventstore']['url'] + "/" + "priceCheck" + "?start_timestamp=" + last_updated_format + "&end_timestamp=" + current_time_format
            )
        price_data = res_price.json()
        price_price = []
        
        for item in price_data:
            price_price.append(float(item['price']))
            
        bs = Stats(
        len(buy_price),
        len(price_price),
        max(buy_price),
        max(price_price),
        min(buy_price),
        min(price_price),
        time
        )
        
        session.add(bs)
        session.commit()
        session.close()
        return NoContent, 201

def init_scheduler():
    """ initialize the scheduler to run periodically"""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
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
    app.run(port=8100)
