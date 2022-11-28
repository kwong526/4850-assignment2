from time import strftime
import uuid
import connexion
from connexion import NoContent
import datetime
import requests
import json
import yaml
import logging, logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
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

def get_health_check():
    """return 200 status if its running"""
    return 200

def get_buy_stock(index):
    """buy the stock"""
    count = 0
    while count < app_config['log']['max_retry']:
        server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
        client = KafkaClient(hosts=server)
        topic = client.topics[str.encode(app_config["events"]["topic"])]

        consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)

        logger.info("Retrieving buy at index %d" % index)
        i = 0
        try:
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                payload = msg["payload"]       
                if msg["type"] == "BuyEvent":
                    if i == index:
                        return payload, 201
                    i += 1
        except:
            logger.error("No more messages found")
            count += 1
        
        logger.error("Could not find buy at index %d" % index)

        return { "message": "Not Found"}, 404

def get_stock_price(index):
    """get the stock price"""
    count = 0
    while count < app_config['log']['max_retry']:
        server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
        client = KafkaClient(hosts=server)
        topic = client.topics[str.encode(app_config["events"]["topic"])]

        consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)

        logger.info("Retrieving buy at index %d" % index)
        i = 0
        try:
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                payload = msg["payload"] 
                if msg["type"] == "PriceEvent":
                    if i == index:
                        return payload, 201
                    i += 1
        except:
            logger.error("No more messages found")
            count += 1

        logger.error("Could not find search at index %d" % index)

        return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8110)