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
    FeatureNotImplemented, EntityNotFound,
    OperationNotPermited, FeatureNotAvailable
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
        logger.debug("Received %s: %s" % (name, _values))
        return _values

    def _generic_delete_(self, name, model, value):
        logger.debug("Deleting %s from %s" % (value, name))
        ss = session.query(model).filter_by(**value).first()
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Successful deletion of %s from %s" % (value, name))
        return True

    def _generic_info_(self, name, model, value):
        logger.debug("Getting %s info by %s" % (name, value))
        ss = session.query(model).filter_by(**value).first()
        if not ss:
            raise EntityNotFound(name.capitalize(), value)
        data = ss.to_dict()
        logger.debug("Received %s from [%s]" % (data, value))
        return data

    def _generic_list_by_something_(self, name, model, value):
        logger.debug("Getting %s by %s" % (name, value))
        ss = session.query(model).filter_by(**value).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict()
            )
        logger.debug("Received %s: %s from [%s]" % (name, _values, value))
        return _values

    def _get_data_device_(self, id):
        logger.debug("Getting device data %s" % id)
        device = self.device_info(id)
        zone = self.zone_info(device['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received device: %s zone: %s "
            "datacenter: %s from [%s]" %
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
        logger.debug("Received ip: %s vlan: %s zone: %s "
            "datacenter: %s from [%s]" %
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

    def _get_data_anycastip_(self, id):
        logger.debug("Getting ip anycast data %s" % id)
        ip = self.Anycastip_info(id)
        anycast = self.anycast_info(ip['anycast_id'])
        logger.debug("Received anycast: %s from [%s]" %
            (anycast, id)
        )
        return {
            'Anycastip': ip['ip'],
            'anycast': anycast['cidr'],
            'anycast_id': anycast['id'],
        }

    def _get_data_subnet_(self, id):
        logger.debug("Getting subnet data %s" % id)
        subnet = self.subnet_info(id)
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received subnet: %s vlan: %s "
            "zone: %s datacenter: %s from [%s]" %
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
            'anycastips': self.anycastips_list_by_anycast(id)
        }

    def _get_data_vlan_(self, id):
        logger.debug("Getting vlan data %s" % id)
        vlan = self.vlan_info(id)
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received vlan: %s zone: %s "
            "datacenter: %s from [%s]" % (vlan, zone, datacenter, id)
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
        logger.debug("Received zone: %s datacenter: %s from [%s]" %
            (zone, datacenter, id)
        )
        return {
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
            'vlans': [ self._get_data_vlan_(vlan['id'])
                       for vlan in self.vlan_list_by_zone(id) ]
        }

    def _get_data_datacenter_(self, id):
        logger.debug("Getting datacenter data %s" % id)
        datacenter = self.datacenter_info(id)
        logger.debug("Received datacenter: %s from [%s]" %
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
        return self._generic_list_("datacenters", models.Datacenter)

    def datacenter_create(self, data):
        logger.debug("Creating datacenter using data: %s" % data)
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
        logger.debug("Created datacenter using data: %s" % data)
        return self.datacenter_info_by_name(data['name'])

    def datacenter_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def datacenter_info(self, id):
        return self._generic_info_("datacenter", models.Datacenter, {'id': id})

    def datacenter_info_by_name(self, name):
        return self._genreric_info_(
            "datacenter", models.Datacenter, {'name': name}
        )

    def datacenter_delete(self, id):
        return self._generic_delete_("datacenter", models.Datacenter, {'id': id})

    def zone_list(self):
        return self._generic_list_("zones", models.Zone)

    def zone_create(self, datacenter_id, data):
        logger.debug("Creating zone on datacenter: %s using data: %s" %
            (datacenter_id, data)
        )
        session.begin(subtransactions=True)
        try:
            session.add(models.Zone(
                name=data['name'], datacenter_id=datacenter_id)
            )
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Zone', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created zone on datacenter: %s using data: %s" %
            (datacenter_id, data)
        )
        return self.zone_info_by_name(data['name'])

    def zone_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def zone_info(self, id):
        return self._generic_info_("zone", models.Zone, {'id': id})

    def zone_info_by_name(self, name):
        return self._genreric_info_(
            "zone", models.Zone, {'name': name}
        )

    def zone_delete(self, id):
        return self._generic_delete_("zone", models.Zone, {'id': id})

    def device_list(self):
        return self._generic_list_("devices", models.Device)

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
        logger.debug("Successful adding vlan to device:"
            " %s device status: %s" % (device_id, _data)
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
        return self._generic_list_by_something_(
            "devices by vlan", models.Vlans_to_Device, {'vlan_id': vlan_id}
        )

    def device_list_by_anycast(self, anycast_id):
        return self._generic_list_by_something_(
            "devices by anycast", models.Anycasts_to_Device,
            {'anycast_id': anycast_id}
        )

    def device_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "devices by zone", models.Device, {'zone_id': zone_id}
        )

    def device_remove_vlan(self, device_id, vlan_id):
        return self._generic_delete_(
            "vlan from device", models.Vlans_to_Device,
            {'vlan_id': vlan_id, 'device_id': device_id}
        )

    def device_remove_anycast(self, device_id, vlan_id):
        return self._generic_delete_(
            "vlan from device", models.Anycasts_to_Device,
            {'vlan_id': vlan_id, 'device_id': device_id}
        )

    def device_info(self, id):
        return self._generic_info_("device", models.Device, {'id': id})

    def device_info_by_name(self, name):
        return self._genreric_info_(
            "device", models.Device, {'name': name}
        )

    def device_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def device_delete(self, id):
        return self._generic_delete_("device", models.Device, {'id': id})

    def vlan_list(self):
        return self._generic_list_("vlans", models.Vlan)

    def vlan_list_by_device(self, device_id):
        return self._generic_list_by_something_(
            "vlans by device", models.Vlans_to_Device,
            {'device_id': device_id}
        )

    def vlan_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "vlans by zone", models.Vlan, {'zone_id': zone_id}
        )

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
        return self._generic_info_("vlan", models.Vlan, {'id': id})

    def vlan_info_by_name(self, name):
        return self._genreric_info_(
            "vlan", models.Vlan, {'name': name}
        )

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_delete(self, id):
        return self._generic_delete_("vlan", models.Vlan, {'id': id})

    def subnet_list(self):
        return self._generic_list_("subnets", models.Subnet)

    def anycast_list(self):
        return self._generic_list_("anycasts", models.Anycast)

    def anycast_list_by_device(self, device_id):
        return self._generic_list_by_something_(
            "anycasts by device", models.Anycasts_to_Device,
            {'device_id': device_id}
        )

    def subnet_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "subnets by vlan", models.Subnet,
            {'vlan_id': vlan_id}
        )

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
        return self._genreric_info_(
            "anycast", models.Anycast, {'cidr': cidr.replace('_','/')}
        )

    def subnet_info(self, id):
        return self._generic_info_("subnet", models.Subnet, {'id': id})

    def anycast_info(self, id):
        return self._generic_info_("anycast", models.Anycast, {'id': id})

    def subnet_info_by_cidr(self, cidr):
        return self._genreric_info_(
            "subnet", models.Subnet, {'cidr': cidr.replace('_','/')}
        )

    def subnet_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_delete(self, id):
        return self._generic_delete_("subnet", models.Subnet, {'id': id})

    def anycast_delete(self, id):
        return self._generic_delete_("anycast", models.Anycast, {'id': id})

    def ip_list(self):
        return self._generic_list_("ips", models.Ip)

    def ip_list_by_subnet(self, subnet_id):
        return self._genreric_info_(
            "ip info by subnet", models.Ip, {'subnet_id': subnet_id}
        )

    def anycastips_list_by_anycast(self, anycast_id):
        return self._generic_list_by_something_(
            "ip info by anycast", models.Anycastip, {'anycast_id': anycast_id}
        )

    def anycastip_list(self):
        return self._generic_list_("ips anycast", models.Anycastip)

    def ip_create(self, subnet_id, data):
        logger.debug("Creating ip on subnet: %s using data: %s" %
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
        logger.debug("Created ip on subnet: %s using data: %s" %
            (subnet_id, data)
        )
        return self.ip_info_by_ip(data['ip'])

    def anycastip_create(self, anycast_id, data):
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
            session.add(
                models.Anycastip(ip=data['ip'], anycast_id=anycast_id)
            )
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['ip']
            raise OperationNotPermited('Anycastip', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        return self.anycastips_info_by_ip(data['ip'])

    def ip_info(self, id):
        return self._generic_info_("ip", models.Ip, {'id': id})

    def anycastips_info(self, id):
        return self._generic_info_("ip anycast", models.Anycastip, {'id': id})

    def ip_info_by_ip(self, ip):
        return self._genreric_info_("ip", models.Ip, {'ip': ip})

    def anycastips_info_by_ip(self, ip):
        return self._genreric_info_(
            "ip anycast", models.Anycastip, {'ip': ip}
        )

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_delete(self, id):
        return self._generic_delete_("ip", models.Ip, {'id': id})

    def anycastips_delete(self, id):
        return self._generic_delete_("ip anycast", models.Anycastip, {'id': id})

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
