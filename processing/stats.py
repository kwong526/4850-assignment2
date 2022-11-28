from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_buy_readings = Column(Integer, nullable=False)
    num_search_readings = Column(Integer, nullable=False)
    max_buy_readings = Column(Integer, nullable=False)
    max_search_readings = Column(Integer, nullable=False)
    min_buy_readings = Column(Integer, nullable=False)
    min_search_readings = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)



    def __init__(self, num_buy_readings, num_search_readings, 
    max_buy_readings, max_search_readings, min_buy_readings,
    min_search_readings, last_updated):
        """ Initializes a processing statistics objet """
        self.num_buy_readings = num_buy_readings
        self.num_search_readings = num_search_readings
        self.max_buy_readings = max_buy_readings
        self.max_search_readings = max_search_readings
        self.min_buy_readings = min_buy_readings
        self.min_search_readings = min_search_readings
        self.last_updated = last_updated


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['id'] = self.id
        dict['num_buy_readings'] = self.num_buy_readings
        dict['num_search_readings'] = self.num_search_readings
        dict['max_buy_readings'] = self.max_buy_readings
        dict['max_search_readings'] = self.max_search_readings
        dict['min_buy_readings'] = self.min_buy_readings
        dict['min_search_readings'] = self.min_search_readings
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        return dict