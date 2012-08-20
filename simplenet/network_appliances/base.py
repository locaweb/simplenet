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

import logging

from simplenet.views.format_view import FormatView
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotImplemented, EntityNotFound, OperationNotPermited
)
from sqlalchemy.exc import IntegrityError

LOG = logging.getLogger(__name__)
session = db_utils.get_database_session()


class SimpleNet(object):

    def __init__(self):
        self.format_for = FormatView()

    def neighborhood_list(self):
        ss = session.query(models.Neighborhood).all()
        neighborhoods = []
        for neighborhood in ss:
            neighborhoods.append(
                self.format_for.neighborhood(
                    neighborhood.id,
                    neighborhood.name
                )
            )
        return neighborhoods

    def neighborhood_create(self, data):
        if not 'name' in data:
            raise Exception('Missing name on request')
        session.begin(subtransactions=True)
        try:
            session.add(models.Neighborhood(name=data['name']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Neighborhood', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.neighborhood_info_by_name(data['name'])

    def neighborhood_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_info(self, id):
        ss = session.query(models.Neighborhood).get(id)
        if not ss:
            raise EntityNotFound('Neighborhood', id)
        return self.format_for.neighborhood(ss.id, ss.name)

    def neighborhood_info_by_name(self, name):
        ss = session.query(models.Neighborhood).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Neighborhood', name)
        return self.format_for.neighborhood(ss.id, ss.name)

    def neighborhood_delete(self, id):
        ss = session.query(models.Neighborhood).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def device_list(self):
        ss = session.query(models.Device).all()
        devices = []
        for device in ss:
            devices.append(
                self.format_for.device(
                    device.id,
                    device.name,
                    device.neighborhood_id
                )
            )
        return devices

    def device_create(self, neighborhood_id, data):
        if not 'name' in data:
            raise Exception('Missing name on request')
        session.begin(subtransactions=True)
        try:
            session.add(models.Device(name=data['name'], neighborhood_id=neighborhood_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Device', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.device_info_by_name(data['name'])

    def device_add_vlan(self, device_id, data):
        if not 'vlan_id' in data:
            raise Exception('Missing name on request')
        session.begin(subtransactions=True)
        try:
            device = session.query(models.Device).get(device_id)
            vlan = session.query(models.Vlan).get(data['vlan_id'])
            relationship = models.Vlans_to_Device()
            relationship.vlan = vlan
            device.vlans_to_devices.append(relationship)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.format_for.device(device.id, device.name, device.neighborhood_id)

    def device_remove_vlan(self, device_id, vlan_id):
        session.begin(subtransactions=True)
        try:
            session.query(models.Vlans_to_Device).filter_by(vlan_id=vlan_id, device_id=device_id).delete()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e.__str__())
        return True

    def device_info(self, id):
        ss = session.query(models.Device).get(id)
        if not ss:
            raise EntityNotFound('Device', id)
        return self.format_for.device(ss.id, ss.name)

    def device_info_by_name(self, name):
        ss = session.query(models.Device).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Device', name)
        return self.format_for.device(ss.id, ss.name, ss.neighborhood_id)

    def device_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def device_delete(self, id):
        ss = session.query(models.Device).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def vlan_list(self):
        ss = session.query(models.Vlan).all()
        vlans = []
        for vlan in ss:
            vlans.append(
                self.format_for.vlan(
                    vlan.id,
                    vlan.name,
                    vlan.neighborhood_id
                )
            )
        return vlans

    def vlan_create(self, neighborhood_id, data):
        if not 'name' in data:
            raise Exception('Missing name on request')
        session.begin(subtransactions=True)
        try:
            session.add(models.Vlan(name=data['name'], neighborhood_id=neighborhood_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Vlan', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.vlan_info_by_name(data['name'])

    def vlan_info(self, id):
        ss = session.query(models.Vlan).get(id)
        if not ss:
            raise EntityNotFound('Vlan', id)
        return self.format_for.vlan(ss.id, ss.name)

    def vlan_info_by_name(self, name):
        ss = session.query(models.Vlan).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Vlan', name)
        return self.format_for.vlan(ss.id, ss.name, ss.neighborhood_id)

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_delete(self, id):
        ss = session.query(models.Vlan).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def subnet_list(self):
        ss = session.query(models.Subnet).all()
        subnets = []
        for subnet in ss:
            subnets.append(
                self.format_for.subnet(
                    subnet.id,
                    subnet.cidr,
                    subnet.vlan_id
                )
            )
        return subnets

    def subnet_create(self, vlan_id, data):
        if not 'cidr' in data:
            raise Exception('Missing cidr on request')
        session.begin(subtransactions=True)
        try:
            session.add(models.Subnet(cidr=data['cidr'], vlan_id=vlan_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['cidr']
            raise OperationNotPermited('Subnet', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.subnet_info_by_cidr(data['cidr'])

    def subnet_info(self, id):
        ss = session.query(models.Subnet).get(id)
        if not ss:
            raise EntityNotFound('Subnet', id)
        return self.format_for.subnet(ss.id, ss.cidr, ss.vlan_id)

    def subnet_info_by_cidr(self, cidr):
        cidr = cidr.replace('_', '/')
        ss = session.query(models.Subnet).filter_by(cidr=cidr).first()
        if not ss:
            raise EntityNotFound('Subnet', cidr)
        return self.format_for.subnet(ss.id, ss.cidr, ss.vlan_id)

    def subnet_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_delete(self, id):
        ss = session.query(models.Subnet).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def ip_list(self):
        ss = session.query(models.Ip).all()
        ips = []
        for ip in ss:
            ips.append(
                self.format_for.ip(
                    ip.id,
                    ip.ip,
                    ip.subnet_id
                )
            )
        return ips

    def ip_create(self, subnet_id, data):
        if not 'ip' in data:
            raise Exception('Missing ip on request')
        session.begin(subtransactions=True)
        try:
            session.add(models.Ip(ip=data['ip'], subnet_id=subnet_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['ip']
            raise OperationNotPermited('Ip', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.ip_info_by_ip(data['ip'])

    def ip_info(self, id):
        ss = session.query(models.Ip).get(id)
        if not ss:
            raise EntityNotFound('Ip', id)
        return self.format_for.ip(ss.id, ss.ip, ss.subnet_id)

    def ip_info_by_ip(self, ip):
        ss = session.query(models.Ip).filter_by(ip=ip).first()
        if not ss:
            raise EntityNotFound('Ip', ip)
        return self.format_for.subnet(ss.id, ss.ip, ss.subnet_id)

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_delete(self, id):
        ss = session.query(models.Ip).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def policy_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()

class Net(SimpleNet):
    pass
