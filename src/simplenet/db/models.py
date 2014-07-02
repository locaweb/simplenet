# Copyright 2012 Locaweb.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @author: Juliano Martinez (ncode), Locaweb.
# @author: Luiz Ozaki, Locaweb.

import uuid

from ipaddr import IPv4Network, IPv4Address, IPv6Network, IPv6Address, IPNetwork, IPAddress

from sqlalchemy import event, Column, Integer, String, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref

from simplenet.common.config import config

Base = declarative_base()

def new_model(model_name):
    model = globals()[model_name]
    return model, model.__tablename__

class Prober(Base):

    __tablename__ = 'prober'
    id = Column(String(36), primary_key=True)
    foo = Column(String(1))


class Datacenter(Base):

    __tablename__ = 'datacenters'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))

    def __init__(self, name, description=''):
        self.id = str(uuid.uuid4())
        self.name = name

    def __repr__(self):
       return "<Datacenter('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return { 'id': self.id, 'name': self.name }


class Zone(Base):

    __tablename__ = 'zones'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    datacenter_id = Column(String(36), ForeignKey('datacenters.id'))
    datacenter = relationship('Datacenter')

    def __init__(self, name, datacenter_id, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.datacenter_id = datacenter_id

    def __repr__(self):
       return "<Zone('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'datacenter': self.datacenter.name,
            'datacenter_id': self.datacenter_id,
        }

class Dhcp(Base):

    __tablename__ = 'dhcps'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    vlans_to_dhcps = relationship('Vlans_to_Dhcp', cascade='all, delete-orphan')

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name

    def __repr__(self):
       return "<Dhcp('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Vlans_to_Dhcp(Base):

    __tablename__ = 'vlans_to_dhcps'

    vlan_id = Column(String(36), ForeignKey('vlans.id'), primary_key=True)
    dhcp_id = Column(String(36), ForeignKey('dhcps.id'), primary_key=True)
    vlan = relationship('Vlan')
    dhcp = relationship('Dhcp')

    def to_dict(self):
        return {
            'vlan_id': self.vlan_id,
            'dhcp_id': self.dhcp_id,
            'vlan': self.vlan.name,
            'name': self.dhcp.name,
        }


class Firewall(Base):

    __tablename__ = 'firewalls'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    status = Column(Boolean())
    description = Column(String(255))
    zone_id = Column(String(36), ForeignKey('zones.id'))
    mac = Column(String(30))
    address = Column(String(255))
    anycasts_to_firewalls = relationship('Anycasts_to_Firewall', cascade='all, delete-orphan')
    zone = relationship('Zone')

    def __init__(self, name, zone_id, mac, status, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.zone_id = zone_id
        self.description = description
        self.mac = mac
        self.status = status

    def __repr__(self):
       return "<Firewall('%s','%s')>" % (self.id, self.name)

    def disable(self):
        self.status = False

    def enable(self):
        self.status = True

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'zone': self.zone.name,
            'zone_id': self.zone_id,
            'mac': self.mac,
            'address': self.address,
            'status': self.status,
        }

    def tree_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'zone': self.zone.name,
            'zone_id': self.zone_id,
            'mac': self.mac,
            'address': self.address,
            'status': self.status,
        }

class Switch(Base):

    __tablename__ = 'switches'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    model_type = Column(String(100))
    mac = Column(String(30))
    address = Column(String(255))
    ports = relationship('Interface', cascade='all, delete-orphan')

    def __init__(self, name, mac='', address='', model_type=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.mac = mac
        self.address = address
        self.model_type = model_type

    def __repr__(self):
       return "<Switch('%s','%s','%s','%s', '%s')>" % (self.id, self.name, self.model_type, self.mac, self.address)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'mac': self.mac,
            'address': self.address,
        }

    def tree_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'mac': self.mac,
            'address': self.address,
        }

class Interface(Base):

    __tablename__ = 'interfaces'

    id = Column(String(36), primary_key=True, unique=True)
    switch_id = Column(String(36), ForeignKey('switches.id'))
    vlan_id = Column(String(36), ForeignKey('vlans.id'))
    status = Column(String(100))
    name = Column(String(255))
    hostname = Column(String(255))
    vlan = relationship('Vlan', backref='interface')
    switch = relationship('Switch')

    def __init__(self, id, hostname):
        self.id = id
        self.hostname = hostname

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'vlan_id': self.vlan.id if self.vlan else None,
            'switch_id': self.switch.id if self.switch else None,
            'ips': [x.to_dict()['ip'] for x in self.ips],
        }

    def tree_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'status': self.status,
            'vlan_id': self.vlan.tree_dict() if self.vlan else None,
            'switch_id': self.switch.tree_dict() if self.switch else None,
            'ips': [x.tree_dict() for x in self.ips],
        }


class Vlan(Base):

    __tablename__ = 'vlans'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True)
    type = Column(String(100))
    vlan_num = Column(Integer())
    description = Column(String(255))
    zone_id = Column(String(36), ForeignKey('zones.id'))
    zone = relationship('Zone')

    def __init__(self, name, zone_id, type, vlan_num, description=''):
        self.id = str(uuid.uuid4())
        self.name = name
        self.zone_id = zone_id
        self.type = type
        self.vlan_num = vlan_num

    def __repr__(self):
       return "<Vlan('%s','%s')>" % (self.id, self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'vlan_num': self.vlan_num,
            'zone': self.zone.name,
            'zone_id': self.zone_id,
        }

    def tree_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'vlan_num': self.vlan_num,
            'name': self.name,
            'zone_id': self.zone_id,
        }

class Anycasts_to_Firewall(Base):

    __tablename__ = 'anycasts_to_firewalls'

    anycast_id = Column(String(36), ForeignKey('anycasts.id'), primary_key=True)
    firewall_id = Column(String(36), ForeignKey('firewalls.id'), primary_key=True)
    description = Column(String(255))
    anycast = relationship('Anycast')
    firewall = relationship('Firewall')

    def to_dict(self):
        return {
            'anycast_id': self.anycast_id,
            'anycast_cidr': self.anycast.cidr,
        }

class Subnet(Base):

    __tablename__ = 'subnets'

    id = Column(String(36), primary_key=True)
    cidr = Column(String(255), unique=True)
    description = Column(String(255))
    vlan_id = Column(String(36), ForeignKey('vlans.id'))
    vlan = relationship('Vlan', backref="subnet")
    ip = relationship('Ip')

    def __init__(self, cidr, vlan_id, description=''):
        self.id = str(uuid.uuid4())
        self.cidr = cidr
        self.vlan_id = vlan_id

    def gateway(self):
        return str(IPNetwork(self.cidr).ip+1)

    def network(self):
        return IPNetwork(self.cidr).with_netmask

    def to_ip(self):
        if IPNetwork(self.cidr).version == 4:
            return IPv4Network(self.cidr)
        else:
            return IPv6Network(self.cidr)

    def contains(self, ip):
        if IPAddress(ip).version == 4:
            return self.to_ip().Contains(IPv4Address(ip))
        else:
            return self.to_ip().Contains(IPv6Address(ip))

    def __repr__(self):
       return "<Subnet('%s','%s')>" % (self.id, self.cidr)

    def to_dict(self):
        return {
            'id': self.id,
            'cidr': self.cidr,
            'vlan': self.vlan.name,
            'vlan_id': self.vlan_id,
            'gateway': self.gateway(),
            'network': self.network(),
            'ips': [x.to_dict() for x in self.ip]
        }

    def tree_dict(self):
        return {
            'id': self.id,
            'cidr': self.cidr,
            'vlan': self.vlan.tree_dict(),
        }

class Ip(Base):

    __tablename__ = 'ips'

    id = Column(String(36), primary_key=True)
    ip = Column(String(255), unique=True)
    description = Column(String(255))
    subnet_id = Column(String(36), ForeignKey('subnets.id'))
    subnet = relationship('Subnet')
    interface_id = Column(String(36), ForeignKey('interfaces.id'))
    interface = relationship("Interface", collection_class=set, backref=backref("ips", collection_class=set))

    def __init__(self, ip, subnet_id, description=''):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.subnet_id = subnet_id

    def __repr__(self):
       return "<Ip('%s','%s','%s')>" % (self.id, self.ip, self.interface_id)

    def to_dict(self):
        hostname = self.interface.hostname if self.interface else None
        return {
            'id': self.id,
            'ip': self.ip,
            'subnet': self.subnet.cidr,
            'subnet_id': self.subnet_id,
            'interface_id': self.interface_id,
            'hostname': hostname,
        }

    def tree_dict(self):
        hostname = self.interface.hostname if self.interface else None
        return {
            'id': self.id,
            'ip': self.ip,
            'hostname': hostname,
            'subnet': self.subnet.tree_dict()
        }

class Anycast(Base):

    __tablename__ = 'anycasts'

    id = Column(String(36), primary_key=True)
    cidr = Column(String(255), unique=True)
    description = Column(String(255))

    def __init__(self, cidr, description=''):
        self.id = str(uuid.uuid4())
        self.cidr = cidr

    def to_ip(self):
        if IPNetwork(self.cidr).version == 4:
            return IPv4Network(self.cidr)
        else:
            return IPv6Network(self.cidr)

    def contains(self, ip):
        if IPAddress(ip).version == 4:
            return self.to_ip().Contains(IPv4Address(ip))
        else:
            return self.to_ip().Contains(IPv6Address(ip))

    def __repr__(self):
       return "<Anycast('%s','%s')>" % (self.id, self.cidr)

    def to_dict(self):
        return {
            'id': self.id,
            'cidr': self.cidr,
        }


class Anycastip(Base):

    __tablename__ = 'anycastips'

    id = Column(String(36), primary_key=True)
    ip = Column(String(255), unique=True)
    description = Column(String(255))
    anycast_id = Column(String(36), ForeignKey('anycasts.id'))
    anycast = relationship('Anycast')

    def __init__(self, ip, anycast_id, description=''):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.anycast_id = anycast_id

    def __repr__(self):
       return "<Anycastip('%s','%s')>" % (self.id, self.ip)

    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'anycast': self.anycast.cidr,
            'anycast_id': self.anycast_id,
        }


class Policy(Base):

    __tablename__ = 'policies'

    id = Column(String(36), primary_key=True)
    proto = Column(String(30), server_default="")
    src = Column(String(100), server_default="")
    src_port = Column(String(100), server_default="")
    dst = Column(String(100), server_default="")
    dst_port = Column(String(100), server_default="")
    table = Column(String(50), server_default="")
    policy = Column(String(50), server_default="")
    in_iface = Column(String(50), server_default="")
    out_iface = Column(String(50), server_default="")
    owner_type = Column(String(50), server_default="")
    status = Column(String(50), server_default="")
    owner_id = Column(String(46), index=True)

    __table_args__  = (UniqueConstraint("proto", "src", "src_port", "dst", "dst_port", "table", "policy", "in_iface", "out_iface", "owner_type", "owner_id"),)
    __mapper_args__ = {'polymorphic_on': owner_type}

    def __init__(self, **kwargs):
        self.id = str(uuid.uuid4())
        self.proto = kwargs['proto']
        self.src = kwargs['src']
        self.src_port = kwargs['src_port']
        self.dst = kwargs['dst']
        self.dst_port = kwargs['dst_port']
        self.table = kwargs['table']
        self.policy = kwargs['policy']
        self.owner_id = kwargs['owner_id']
        self.status = kwargs.get('status', 'PENDING')


class DatacenterPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'datacenter'}

    datacenter = relationship('Datacenter', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Datacenter.id)

    def __init__(self, **kwargs):
        super(DatacenterPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.datacenter.name }


class ZonePolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'zone'}

    zone = relationship('Zone', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Zone.id)

    def __init__(self, **kwargs):
        super(ZonePolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.zone.name }


class VlanPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'vlan'}

    vlan = relationship('Vlan', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Vlan.id)

    def __init__(self, **kwargs):
        super(VlanPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.vlan.name }


class AnycastPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'anycast'}

    anycast = relationship('Anycast', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Anycast.id)

    def __init__(self, **kwargs):
        super(AnycastPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.anycast.cidr }


class SubnetPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'subnet'}

    subnet = relationship('Subnet', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Subnet.id)

    def __init__(self, **kwargs):
        super(SubnetPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.subnet.cidr }


class AnycastipPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'anycastip'}

    ip = relationship('Anycastip', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Anycastip.id)

    def __init__(self, **kwargs):
        super(AnycastipPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.ip.ip }


class IpPolicy(Policy):

    __mapper_args__ = {'polymorphic_identity': 'ip'}

    ip = relationship('Ip', foreign_keys=Policy.owner_id, primaryjoin=Policy.owner_id == Ip.id)

    def __init__(self, **kwargs):
        super(IpPolicy, self).__init__(**kwargs)

    def to_dict(self):
        return { 'id': self.id,
                 'owner_id': self.owner_id,
                 'proto': self.proto,
                 'src': self.src,
                 'src_port': self.src_port,
                 'dst': self.dst,
                 'dst_port': self.dst_port,
                 'table': self.table,
                 'policy': self.policy,
                 'status': self.status,
                 'owner': self.ip.ip }


database_type = config.get('server', 'database_type')
database_name = config.get('server', 'database_name')

engine = None
if 'sqlite' in database_type:
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    engine = create_engine('%s:///%s' % (database_type, database_name))
    event.listen(engine, 'connect', _fk_pragma_on_connect)
else:
    database_user = config.get('server', 'database_user')
    database_pass = config.get('server', 'database_pass')
    database_host = config.get('server', 'database_host')
    engine = create_engine("%s://%s:%s@%s/%s" % (database_type,
                            database_user,
                            database_pass,
                            database_host,
                            database_name),
                            pool_size=10,
                            max_overflow=4,
                            pool_recycle=120)

Base.metadata.create_all(engine)
