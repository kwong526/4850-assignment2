from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Health(Base):
    """ Processing Statistics """
    __tablename__ = "health"
    id = Column(Integer, primary_key=True)
    receiver = Column(String(10), nullable=False)
    storage = Column(String(10), nullable=False)
    processing = Column(String(10), nullable=False)
    audit = Column(String(10), nullable=False)
    last_updated = Column(DateTime, nullable=False)



    def __init__(self, receiver, storage, 
    processing, audit, last_updated):
        """ Initializes a processing statistics objet """
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit = audit
        self.last_updated = last_updated


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['id'] = self.id
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit'] = self.audit
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        return dict