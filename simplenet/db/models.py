#!/usr/bin/python

import uuid

from ipaddr import IPv4Network, IPv4Address

from sqlalchemy import Column, String, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

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

class Device(Base):

    __tablename__ = 'devices'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    neighborhood_id = Column(String(255), ForeignKey('neighborhoods.id'))
    vlans_to_devices = relationship("Vlans_to_Device")

    def __init__(self, name, neighborhood_id, description=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.neighborhood_id = neighborhood_id

    def __repr__(self):
       return "<Device('%s','%s')>" % (self.id, self.name)

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

class Vlans_to_Device(Base):
    __tablename__ = 'vlans_to_devices'
    vlan_id = Column(String(255), ForeignKey('vlans.id'), primary_key=True)
    device_id = Column(String(255), ForeignKey('devices.id'), primary_key=True)
    description = Column(String(255))
    child = relationship("Vlan")

class Subnet(Base):

    __tablename__ = 'subnets'

    id = Column(String(255), primary_key=True)
    cidr = Column(String(255), unique=True)
    description = Column(String(255))
    vlan_id = Column(String(255), ForeignKey('vlans.id'))

    def __init__(self, cidr, vlan_id, description=""):
        self.id = str(uuid.uuid4())
        self.cidr = cidr
        self.vlan_id = vlan_id

    def to_ip(self):
        return IPv4Network(self.cidr)

    def contains(self, ip):
        return self.to_ip().Contains(IPv4Address(ip))

    def __repr__(self):
       return "<Subnet('%s','%s')>" % (self.id, self.cidr)

class Ip(Base):

    __tablename__ = 'ips'

    id = Column(String(255), primary_key=True)
    ip = Column(String(255), unique=True)
    description = Column(String(255))
    subnet_id = Column(String(255), ForeignKey('subnets.id'))

    def __init__(self, cidr, vlan_id, description=""):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.subnet_id = subnet_id

    def __repr__(self):
       return "<Ip('%s','%s')>" % (self.id, self.ip)

engine = create_engine('sqlite:////tmp/meh.db')
Base.metadata.create_all(engine)
