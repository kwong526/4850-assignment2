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

def buyStock(body):
    """purchase the item you selected"""
    trace = str(uuid.uuid4())
    body["trace_id"] = trace
    count = 0

    logger.info(f"Returned event buy response {trace}")

    try:
        server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
        client = KafkaClient(hosts=server)
        topic = client.topics[str.encode(app_config["events"]["topic"])]

        producer = topic.get_sync_producer()

        msg = {
            "type": "purchase",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
        }

        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
    except:
        logger.error('connection lost')
        count += 1

    return 201


def stockPrice(body):
    """price the stock"""
    trace = str(uuid.uuid4())
    body["trace_id"] = trace
    count = 0

    logger.info(f"Returned event price response {trace}")

    try:
        server = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
        client = KafkaClient(hosts=server)
        topic = client.topics[str.encode(app_config["events"]["topic"])]

        producer = topic.get_sync_producer()

        msg = {
            "type": "price",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
        }

        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
    except:
        logger.error('connection lost')
        count += 1       
    return 201
    
app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)
