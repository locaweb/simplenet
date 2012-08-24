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

    def _get_parents_ip_(self, id):
        ip = self.ip_info(id)
        subnet = self.subnet_info(ip['subnet_id'])
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        return {
            'subnet_id': ip['subnet_id'],
            'vlan_id': vlan['id'],
            'zone_id': zone['id'],
            'datacenter_id': zone['datacenter_id']
        }

    def _get_parents_subnet_(self, id):
        subnet = self.subnet_info(id)
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        return {
            'vlan_id': vlan['id'],
            'zone_id': zone['id'],
            'datacenter_id': zone['datacenter_id']
        }

    def _get_parents_vlan_(self, id):
        vlan = self.vlan_info(id)
        zone = self.zone_info(vlan['zone_id'])
        return {
            'zone_id': zone['id'],
            'datacenter_id': zone['datacenter_id']
        }

    def _get_parents_zone_(self, id):
        return {
            'datacenter_id': self.zone_info(id)['datacenter_id']
        }

    def datacenter_list(self):
        ss = session.query(models.Datacenter).all()
        datacenters = []
        for datacenter in ss:
            datacenters.append(
                self.format_for.datacenter(
                    datacenter.id,
                    datacenter.name
                )
            )
        return datacenters

    def datacenter_create(self, data):
        session.begin(subtransactions=True)
        try:
            session.add(models.Datacenter(name=data['name']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Datacenter', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.datacenter_info_by_name(data['name'])

    def datacenter_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def datacenter_info(self, id):
        ss = session.query(models.Datacenter).get(id)
        if not ss:
            raise EntityNotFound('Datacenter', id)
        return self.format_for.datacenter(ss.id, ss.name)

    def datacenter_info_by_name(self, name):
        ss = session.query(models.Datacenter).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Datacenter', name)
        return self.format_for.datacenter(ss.id, ss.name)

    def datacenter_delete(self, id):
        ss = session.query(models.Datacenter).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def zone_list(self):
        ss = session.query(models.Zone).all()
        zones = []
        for zone in ss:
            zones.append(
                self.format_for.zone(
                    zone.id,
                    zone.name,
                    zone.datacenter_id
                )
            )
        return zones

    def zone_create(self, datacenter_id, data):
        session.begin(subtransactions=True)
        try:
            session.add(models.Zone(name=data['name'], datacenter_id=datacenter_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Zone', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.zone_info_by_name(data['name'])

    def zone_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def zone_info(self, id):
        ss = session.query(models.Zone).get(id)
        if not ss:
            raise EntityNotFound('Zone', id)
        return self.format_for.zone(ss.id, ss.name, ss.datacenter_id)

    def zone_info_by_name(self, name):
        ss = session.query(models.Zone).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Zone', name)
        return self.format_for.zone(ss.id, ss.name, ss.datacenter_id)

    def zone_delete(self, id):
        ss = session.query(models.Zone).get(id)
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
                    device.zone_id
                )
            )
        return devices

    def device_create(self, zone_id, data):
        session.begin(subtransactions=True)
        try:
            session.add(models.Device(name=data['name'], zone_id=zone_id))
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
        device = session.query(models.Device).get(device_id)
        vlan = session.query(models.Vlan).get(data['vlan_id'])

        if device.zone_id != vlan.zone_id:
            raise OperationNotPermited(
                'Device', 'Device and Vlan must be from the same zone'
            )

        session.begin(subtransactions=True)
        try:
            relationship = models.Vlans_to_Device()
            relationship.vlan = vlan
            device.vlans_to_devices.append(relationship)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self.format_for.device(device.id, device.name, device.zone_id)

    def device_list_device_by_vlan(self, vlan_id):
        ss = session.query(models.Vlans_to_Device).filter_by(vlan_id=vlan_id).all()
        devices = []
        for relationship in ss:
            devices.append(
                self.format_for.device(
                    relationship.device_id,
                    relationship.device.name,
                    relationship.device.zone_id
                )
            )
        return devices

    def device_list_vlans_by_device(self, device_id):
        ss = session.query(models.Vlans_to_Device).filter_by(device_id=device_id).all()
        vlans = []
        for relationship in ss:
            vlans.append(
                self.format_for.vlan(
                    relationship.vlan_id,
                    relationship.vlan.name,
                    relationship.vlan.zone_id
                )
            )
        return vlans

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
        return self.format_for.device(ss.id, ss.name, ss.zone_id)

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
                    vlan.zone_id
                )
            )
        return vlans

    def vlan_create(self, zone_id, data):
        session.begin(subtransactions=True)
        try:
            session.add(models.Vlan(name=data['name'], zone_id=zone_id))
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
        return self.format_for.vlan(ss.id, ss.name, ss.zone_id)

    def vlan_info_by_name(self, name):
        ss = session.query(models.Vlan).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Vlan', name)
        return self.format_for.vlan(ss.id, ss.name, ss.zone_id)

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
        subnet = session.query(models.Subnet).get(subnet_id)
        if not subnet.contains(data['ip']):
            raise OperationNotPermited(
                'Ip', "%s address must be contained in %s" % (
                        data['ip'],
                        subnet.cidr
                )
            )
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
        return self.format_for.ip(ss.id, ss.ip, ss.subnet_id)

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
