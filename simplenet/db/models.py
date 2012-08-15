#!/usr/bin/python

import uuid
from sqlalchemy import Column, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Neighborhood(Base):

    __tablename__ = 'neighborhoods'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))

    def __init__(self, name, description=""):
        self.id = str(uuid.uuid4())
        self.name = name

    def __repr__(self):
       return "<Neighborhood('%s','%s')>" % (self.id, self.name)

class Vlan(Base):

    __tablename__ = 'vlans'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    neighborhood_id = Column(String(255), ForeignKey('neighborhoods.id'))

    def __init__(self, name, neighborhood_id, description=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.neighborhood_id = neighborhood_id

    def __repr__(self):
       return "<Vlan('%s','%s')>" % (self.id, self.name)

engine = create_engine('sqlite:////tmp/meh.db')
Base.metadata.create_all(engine)
