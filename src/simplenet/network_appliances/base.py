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

from simplenet.common.config import config, get_logger
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotImplemented, EntityNotFound, OperationNotPermited
)
from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()

class SimpleNet(object):

    def _generic_list_(self, name, model):
        logger.debug("Listing %s" % name)
        ss = session.query(model).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict(),
            )
        logger.debug("Received %s: %s" % name)
        return _values

    def _generic_info_(self, name, model, id):
        logger.debug("Getting %s info from %s" % (name, id))
        ss = session.query(name).get(id)
        if not ss:
            raise EntityNotFound(nama.capitalize(), id)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, id))
        return data

    def _genreric_info_by_something_(self, name, value, model):
        logger.debug("Getting %s info by %s" % (name, value))
        ss = session.query(model).filter_by(**value).first()
        if not ss:
            raise EntityNotFound(nama.capitalize(), value)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, value))
        return data

    def _get_data_device_(self, id):
        logger.debug("Getting device data %s" % id)
        device = self.device_info(id)
        zone = self.zone_info(device['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received device: %s zone: %s dc: %s from [%s]" %
            (device, zone, datacenter, id)
        )
        return {
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
        }

    def _get_data_ip_(self, id):
        logger.debug("Getting ip data %s" % id)
        ip = self.ip_info(id)
        subnet = self.subnet_info(ip['subnet_id'])
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received ip: %s vlan: %s zone: %s dc: %s from [%s]" %
            (ip, vlan, zone, datacenter, id)
        )
        return {
            'ip': ip['ip'],
            'subnet': subnet['cidr'],
            'subnet_id': subnet['id'],
            'vlan': vlan['name'],
            'vlan_id': vlan['id'],
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
        }

    def _get_data_ipanycast_(self, id):
        logger.debug("Getting ip anycast data %s" % id)
        ip = self.ipanycast_info(id)
        anycast = self.anycast_info(ip['anycast_id'])
        logger.debug("Received anycast: %s from [%s]" %
            (anycast, id)
        )
        return {
            'ipanycast': ip['ip'],
            'anycast': anycast['cidr'],
            'anycast_id': anycast['id'],
        }

    def _get_data_subnet_(self, id):
        logger.debug("Getting subnet data %s" % id)
        subnet = self.subnet_info(id)
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received subnet: %s vlan: %s zone: %s dc: %s from [%s]" %
            (subnet, vlan, zone, datacenter, id)
        )
        return {
            'subnet': subnet['cidr'],
            'vlan': vlan['name'],
            'vlan_id': vlan['id'],
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
            'ips': self.ip_list_by_subnet(id)
        }

    def _get_data_anycast_(self, id):
        logger.debug("Getting anycast data %s" % id)
        anycast = self.anycast_info(id)
        logger.debug("Received anycast: %s from [%s]" %
            (anycast, id)
        )
        return {
            'anycast_id': anycast['id'],
            'anycast': anycast['cidr'],
            'ipsanycast': self.ipsanycast_list_by_anycast(id)
        }

    def _get_data_vlan_(self, id):
        logger.debug("Getting vlan data %s" % id)
        vlan = self.vlan_info(id)
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received vlan: %s zone: %s dc: %s from [%s]" %
            (vlan, zone, datacenter, id)
        )
        return {
            'vlan': vlan['name'],
            'vlan_id': vlan['id'],
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
            'subnets': self.subnet_list_by_vlan(id),
        }

    def _get_data_zone_(self, id):
        logger.debug("Getting zone data %s" % id)
        zone = self.zone_info(id)
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received zone: %s dc: %s from [%s]" %
            (zone, datacenter, id)
        )
        return {
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
            'vlans': [ self._get_data_vlan_(vlan['id']) for vlan in self.vlan_list_by_zone(id) ]
        }

    def _get_data_datacenter_(self, id):
        logger.debug("Getting dc data %s" % id)
        datacenter = self.datacenter_info(id)
        logger.debug("Received dc: %s from [%s]" %
            (datacenter, id)
        )
        return {
            'datacenter': datacenter['name'],
            'zones': self.zone_list_by_datacenter(id),
        }

    def prober(self):
        logger.debug("Getting prober data")
        ss = session.query(models.Prober).all()
        logger.debug("Received prober: %s" % ss)
        return ss

    def datacenter_list(self):
        return self._generic_list_(self, "datacenters", models.Datacenter)

    def datacenter_create(self, data):
        logger.debug("Creating dc using data: %s" % data)
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
        logger.debug("Created dc using data: %s" % data)
        return self.datacenter_info_by_name(data['name'])

    def datacenter_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def datacenter_info(self, id):
        self._generic_info_(self, "datacenter", models.Datacenter, id)

    def datacenter_info_by_name(self, name):
        logger.debug("Getting dc info by name %s" % name)
        ss = session.query(models.Datacenter).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Datacenter', name)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, name))
        return data

    def datacenter_delete(self, id):
        logger.debug("Deleting dc %s" % id)
        ss = session.query(models.Datacenter).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deleted dc %s" % id)
        return True

    def zone_list(self):
        return self._generic_list_(self, "zones", models.Zone)

    def zone_create(self, datacenter_id, data):
        logger.debug("Creating zone on dc: %s using data: %s" %
            (datacenter_id, data)
        )
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
        logger.debug("Created zone on dc: %s using data: %s" %
            (datacenter_id, data)
        )
        return self.zone_info_by_name(data['name'])

    def zone_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def zone_info(self, id):
        self.generic_info(self, "zone", models.Zone, id)

    def zone_info_by_name(self, name):
        logger.debug("Getting zone info by name %s" % name)
        ss = session.query(models.Zone).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Zone', name)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, name))
        return data

    def zone_delete(self, id):
        logger.debug("Deleting zone %s" % id)
        ss = session.query(models.Zone).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deleted zone %s" % id)
        return True

    def device_list(self):
        return self._generic_list_(self, "devices", models.Device)

    def device_create(self, zone_id, data):
        logger.debug("Creating device on zone: %s using data: %s" %
            (zone_id, data)
        )
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
        logger.debug("Created device on zone: %s using data: %s" %
            (zone_id, data)
        )
        return self.device_info_by_name(data['name'])

    def device_add_vlan(self, device_id, data):
        logger.debug("Adding vlan to device: %s using data: %s" %
            (device_id, data)
        )
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
        _data = device.to_dict()
        logger.debug("Successful adding vlan to device: %s device status: %s" %
            (device_id, _data)
        )
        return _data

    def device_add_anycast(self, device_id, data):
        logger.debug("Adding vlan to anycast: %s using data: %s" %
            (device_id, data)
        )
        device = session.query(models.Device).get(device_id)
        anycast = session.query(models.Anycast).get(data['anycast_id'])

        session.begin(subtransactions=True)
        try:
            relationship = models.Anycasts_to_Device()
            relationship.anycast = anycast
            device.anycasts_to_devices.append(relationship)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        _data = device.to_dict()
        logger.debug("Successful adding vlan to anycast: %s device status: %s" %
            (device_id, _data)
        )
        return _data

    def device_list_by_vlan(self, vlan_id):
        logger.debug("Listing devices by vlan [%s]" % vland_id)
        ss = session.query(models.Vlans_to_Device).filter_by(vlan_id=vlan_id).all()
        devices = []
        for relationship in ss:
            devices.append(
                relationship.to_dict()
            )
        logger.debug("Received devices: %s from [%s]" % (devices, vlan_id))
        return devices

    def device_list_by_anycast(self, anycast_id):
        logger.debug("Listing devices by anycast [%s]" % anycast_id)
        ss = session.query(models.Anycasts_to_Device).filter_by(anycast_id=anycast_id).all()
        devices = []
        for relationship in ss:
            devices.append(
                relationship.to_dict()
            )
        logger.debug("Received devices: %s from [%s]" % (devices, anycast_id))
        return devices

    def device_list_by_zone(self, zone_id):
        logger.debug("Listing devices by zone [%s]" % zone_id)
        ss = session.query(models.Device).filter_by(zone_id=zone_id).all()
        devices = []
        for relationship in ss:
            devices.append(
                relationship.to_dict()
            )
        logger.debug("Received devices: %s from [%s]" % (devices, zone_id))
        return devices

    def device_remove_vlan(self, device_id, vlan_id):
        logger.debug("Removing vlan from device: %s vlan: %s" %
            (device_id, vlan_id)
        )
        session.begin(subtransactions=True)
        try:
            session.query(models.Vlans_to_Device).filter_by(vlan_id=vlan_id, device_id=device_id).delete()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e.__str__())
        logger.debug("Successful remotion of vlan %s from device: %s" % (vlan_id, device_id))
        return True

    def device_info(self, id):
        self._generic_info_(self, "device", models.Device, id)

    def device_info_by_name(self, name):
        logger.debug("Getting zone info by name %s" % name)
        ss = session.query(models.Device).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Device', name)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, name))
        return data

    def device_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def device_delete(self, id):
        logger.debug("Deleting device %s" % id)
        ss = session.query(models.Device).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deletion of zone %s" % id)
        return True

    def vlan_list(self):
        return self._generic_list_(self, "vlans", models.Vlan)

    def vlan_list_by_device(self, device_id):
        logger.debug("Listing vlans by device [%s]" % device_id)
        ss = session.query(models.Vlans_to_Device).filter_by(device_id=device_id).all()
        vlans = []
        for relationship in ss:
            vlans.append(
                relationship.to_dict()
            )
        logger.debug("Received vlans: %s" % vlans)
        return vlans

    def vlan_list_by_zone(self, zone_id):
        logger.debug("Listing vlans by zone [%s]" % zone_id)
        ss = session.query(models.Vlan).filter_by(zone_id=zone_id).all()
        vlans = []
        for relationship in ss:
            vlans.append(
                relationship.to_dict()
            )
        logger.debug("Received vlans: %s" % vlans)
        return vlans

    def vlan_create(self, zone_id, data):
        logger.debug("Creating vlan on zone: %s using data: %s" %
            (zone_id, data)
        )
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
        logger.debug("Created vlan on zone: %s using data: %s" %
            (zone_id, data)
        )
        return self.vlan_info_by_name(data['name'])

    def vlan_info(self, id):
        self._generic_info_(self, "vlan", models.Vlan, id)

    def vlan_info_by_name(self, name):
        logger.debug("Getting vlan info by name %s" % name)
        ss = session.query(models.Vlan).filter_by(name=name).first()
        if not ss:
            raise EntityNotFound('Vlan', name)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, name))
        return data

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_delete(self, id):
        logger.debug("Deleting vlan %s" % id)
        ss = session.query(models.Vlan).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deleted vlan %s" % id)
        return True

    def subnet_list(self):
        return self._generic_list_(self, "subnets", models.Subnet)

    def anycast_list(self):
        return self._generic_list_(self, "anycasts", models.Anycast)

    def anycast_list_by_device(self, device_id):
        logger.debug("Listing anycasts by device [%s]" % device_id)
        ss = session.query(models.Anycasts_to_Device).filter_by(device_id=device_id).all()
        anycasts = []
        for relationship in ss:
            anycasts.append(
                relationship.to_dict()
            )
        logger.debug("Received anycasts: %s" % anycasts)
        return anycasts

    def subnet_list_by_vlan(self, vlan_id):
        logger.debug("Listing subnets by vlan [%s]" % vlan_id)
        ss = session.query(models.Subnet).filter_by(vlan_id=vlan_id).all()
        subnets = []
        for subnet in ss:
            subnets.append(
                subnet.to_dict()
            )
        logger.debug("Received subnets: %s" % subnets)
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

    def anycast_create(self, data):
        logger.debug("Creating subnet using data: %s" % data)
        session.begin(subtransactions=True)
        try:
            session.add(models.Anycast(cidr=data['cidr']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['cidr']
            raise OperationNotPermited('Anycast', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created subnet using data: %s" % data)
        return self.anycast_info_by_cidr(data['cidr'])

    def anycast_info_by_cidr(self, cidr):
        logger.debug("Getting anycast by cidr [%s]" % cidr)
        cidr = cidr.replace('_', '/')
        ss = session.query(models.Anycast).filter_by(cidr=cidr).first()
        if not ss:
            raise EntityNotFound('Anycast', cidr)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, name))
        return data

    def subnet_info(self, id):
        self._generic_info_(self, "subnet", models.Subnet, id)

    def anycast_info(self, id):
        self._generic_info_(self, "anycast", models.Anycast, id)

    def subnet_info_by_cidr(self, cidr):
        logger.debug("Getting subnet info from %s" % id)
        cidr = cidr.replace('_', '/')
        ss = session.query(models.Subnet).filter_by(cidr=cidr).first()
        if not ss:
            raise EntityNotFound('Subnet', cidr)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, id))
        return data

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

    def anycast_delete(self, id):
        logger.debug("Deleting anycast %s" % id)
        ss = session.query(models.Anycast).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deleted anycast %s" % id)
        return True

    def ip_list(self):
        return self._generic_list_(self, "ips", models.Ip)

    def ip_list_by_subnet(self, subnet_id):
        logger.debug("Getting ip info by subnet %s" % subnet_id)
        ss = session.query(models.Ip).filter_by(subnet_id=subnet_id).all()
        ips = []
        for ip in ss:
            ips.append(
                ip.to_dict()
            )
        logger.debug("Received ips: %s from [%s]" % (ips, subnet_id))
        return ips

    def ipanycast_list_by_anycast(self, anycast_id):
        logger.debug("Getting ip info by anycast %s" % anycast_id)
        ss = session.query(models.Ipanycast).filter_by(anycast_id=anycast_id).all()
        ips = []
        for ip in ss:
            ips.append(
                ip.to_dict()
            )
        logger.debug("Received ips: %s from [%s]" % (ips, anycast_id))
        return ips

    def ipanycast_list(self):
        return self._generic_list_(self, "ips anycast", models.Ipanycast)

    def ip_create(self, subnet_id, data):
        logger.debug("Creating ip on zone: %s using data: %s" %
            (subnet_id, data)
        )
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
        logger.debug("Created ip on zone: %s using data: %s" %
            (zone_id, data)
        )
        return self.ip_info_by_ip(data['ip'])

    def ipanycast_create(self, anycast_id, data):
        logger.debug("Creating ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        anycast = session.query(models.Anycast).get(anycast_id)
        if not anycast.contains(data['ip']):
            raise OperationNotPermited(
                'Ip', "%s address must be contained in %s" % (
                        data['ip'],
                        anycast.cidr
                )
            )
        session.begin(subtransactions=True)
        try:
            session.add(models.Ipanycast(ip=data['ip'], anycast_id=anycast_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['ip']
            raise OperationNotPermited('Ipanycast', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        return self.ipanycast_info_by_ip(data['ip'])

    def ip_info(self, id):
        self._generic_info_(self, "ip", models.Ip, id)

    def ipanycast_info(self, id):
        self._generic_info_(self, "ip anycast", models.Ipanycast, id)

    def ip_info_by_ip(self, ip):
        logger.debug("Getting ip info by ip %s" % id)
        ss = session.query(models.Ip).filter_by(ip=ip).first()
        if not ss:
            raise EntityNotFound('Ip', ip)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, id))
        return data

    def ipanycast_info_by_ip(self, ip):
        logger.debug("Getting anycast ip info by ip %s" % id)
        ss = session.query(models.Ipanycast).filter_by(ip=ip).first()
        if not ss:
            raise EntityNotFound('Ipanycast', ip)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, id))
        return data

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_delete(self, id):
        logger.debug("Deleting ip %s" % id)
        ss = session.query(models.Ip).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deleted ip %s" % id)
        return True

    def ipanycast_delete(self, id):
        logger.debug("Deleting anycast ip %s" % id)
        ss = session.query(models.Ipanycast).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful anycast ip %s" % id)
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
