#!/usr/bin/python

import uuid

from ipaddr import IPv4Network, IPv4Address

from sqlalchemy import event, Column, String, create_engine, ForeignKey, Table, Integer, Enum
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
    vlans_to_devices = relationship("Vlans_to_Device", cascade='all, delete-orphan')

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
    vlan = relationship("Vlan")


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

    def __init__(self, ip, subnet_id, description=""):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.subnet_id = subnet_id

    def __repr__(self):
       return "<Ip('%s','%s')>" % (self.id, self.ip)


class BasePolicy(Base):

    __tablename__ = 'base_policies'

    uuid = Column(String(255), primary_key=True)
    proto = Column(String(255), nullable=False)
    src = Column(String(255), nullable=False)
    src_port = Column(String(255), nullable=True)
    dst = Column(String(255), nullable=False)
    dst_port = Column(String(255), nullable=True)
    table = Column(String(255), nullable=False)
    policy = Column(String(255), nullable=False)
    description = Column(String(255))

    def __init__(self, parent_id, proto, src, src_port, dst, dst_port, table, policy):
        self.uuid = str(uuid.uuid4())
        self.proto = proto
        self.src = src
        self.src_port = src_port
        self.dst = dst
        self.dst_port = dst_port
        self.direction = direction
        self.table = table
        self.policy = policy
        self.parent_id = parent_id

    def to_dict(self):
        return {'id': self.uuid,
                'parent_id': parent_id,
                'proto': self.proto,
                'src': self.src,
                'src_port': self.src_port,
                'dst': self.dst,
                'dst_port': self.dst_port,
                'table': self.table,
                'policy': self.policy }


class NeighborhoodPolicy(BasePolicy):

    __tablename__ = 'neighborhood_policies'

    parent_id = Column(String(255), ForeignKey('neighborhood.id'))


class VlanPolicy(BasePolicy):

    __tablename__ = 'vlan_policies'

    parent_id = Column(String(255), ForeignKey('vlans.id'))


class SubnetPolicy(BasePolicy):

    __tablename__ = 'subnet_policies'

    parent_id = Column(String(255), ForeignKey('subnet.id'))


class IpPolicy(BasePolicy):

    __tablename__ = 'ip_policies'

    parent_id = Column(String(255), ForeignKey('ip.id'))


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')

engine = create_engine('sqlite:////tmp/meh.db')
event.listen(engine, 'connect', _fk_pragma_on_connect)
Base.metadata.create_all(engine)
