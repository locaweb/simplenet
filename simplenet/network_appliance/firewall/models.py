#!/usr/bin/python

import uuid
from sqlalchemy import Column, String

class Neighborhood(Base):
    __tablename__ = 'neighborhoods'

    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    description = Column(String(255))

    def __init__(self, name, description=""):
        self.id = str(uuid.uuid4())
        self.name = name

    def __repr__(self):
       return "<Neighborhood('%s','%s')>" % (self.id, self.name)
