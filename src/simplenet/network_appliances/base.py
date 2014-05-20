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

from uuid import UUID
from simplenet.common.config import get_logger
from simplenet.common.hooks import post_run
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotAvailable, EntityNotFound,
    OperationNotPermited
)
from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()


class SimpleNet(object):
    @staticmethod
    def valid_uuid(data):
        try:
            UUID(data)
        except ValueError:
            return False

        return True

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
        ip = self.anycastip_info(id)
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
            'anycastips': self.anycastip_list_by_anycast(id)
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

    def firewall_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "firewalls by zone", models.Firewall, {'zone_id': zone_id}
        )

    def datacenter_list(self):
        return self._generic_list_("datacenters", models.Datacenter)

    def datacenter_create(self, data):
        logger.debug("Creating datacenter using data: %s" % data)
        session.begin(subtransactions=True)
        try:
            session.add(models.Datacenter(name=data['name']))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['name']
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Datacenter', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created datacenter using data: %s" % data)
        return self.datacenter_info_by_name(data['name'])

    def datacenter_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def datacenter_info(self, id):
        return self._generic_info_("datacenter", models.Datacenter, {'id': id})

    def datacenter_info_by_name(self, name):
        return self._generic_info_(
            "datacenter", models.Datacenter, {'name': name}
        )

    def datacenter_delete(self, id):
        return self._generic_delete_("datacenter", models.Datacenter, {'id': id})

    def zone_list(self):
        return self._generic_list_("zones", models.Zone)

    def zone_list_by_datacenter(self, datacenter_id):
        return self._generic_list_by_something_(
            "zones by datacenter", models.Zone,
            {'datacenter_id': datacenter_id}
        )

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
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "datacenter_id %s doesnt exist" % datacenter_id
            elif msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['name']
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Zone', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created zone on datacenter: %s using data: %s" %
            (datacenter_id, data)
        )
        return self.zone_info_by_name(data['name'])

    def zone_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def zone_info(self, id):
        return self._generic_info_("zone", models.Zone, {'id': id})

    def zone_info_by_name(self, name):
        return self._generic_info_(
            "zone", models.Zone, {'name': name}
        )

    def zone_delete(self, id):
        return self._generic_delete_("zone", models.Zone, {'id': id})

    def vlan_list(self):
        return self._generic_list_("vlans", models.Vlan)

    def vlan_list_by_firewall(self, firewall_id):
        return self._generic_list_by_something_(
            "vlans by firewall", models.Vlans_to_Firewall,
            {'firewall_id': firewall_id}
        )

    def vlan_list_by_dhcp(self, dhcp_id):
        return self._generic_list_by_something_(
            "vlans by dhcp", models.Vlans_to_Dhcp,
            {'dhcp_id': dhcp_id}
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
            session.add(models.Vlan(name=data['name'], zone_id=zone_id,
                                    type=data['type'], vlan_num=data['vlan_num']))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "zone_id %s doesnt exist" % zone_id
            elif msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['name']
            else:
                forbidden_msg = "Unknown error"
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
        return self._generic_info_(
            "vlan", models.Vlan, {'name': name}
        )

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def vlan_delete(self, id):
        return self._generic_delete_("vlan", models.Vlan, {'id': id})

    def subnet_list(self):
        return self._generic_list_("subnets", models.Subnet)

    def anycast_list(self):
        return self._generic_list_("anycasts", models.Anycast)

    def anycast_list_by_firewall(self, firewall_id):
        return self._generic_list_by_something_(
            "anycasts by firewall", models.Anycasts_to_Firewall,
            {'firewall_id': firewall_id}
        )

    def subnet_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "subnets by vlan", models.Subnet,
            {'vlan_id': vlan_id}
        )

    @post_run
    def subnet_create(self, vlan_id, data):
        session.begin(subtransactions=True)
        try:
            session.add(models.Subnet(cidr=data['cidr'], vlan_id=vlan_id))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "vlan_id %s doesnt exist" % vlan_id
            elif msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['cidr']
            else:
                forbidden_msg = "Unknown error -- %s" % msg
            raise OperationNotPermited('Subnet', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        vlan = session.query(models.Vlan).get(vlan_id)
        #self._enqueue_dhcp_entries_(vlan, 'update')
        return self.subnet_info_by_cidr(data['cidr'])

    def anycast_create(self, data):
        logger.debug("Creating subnet using data: %s" % data)
        session.begin(subtransactions=True)
        try:
            session.add(models.Anycast(cidr=data['cidr']))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['cidr']
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Anycast', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created subnet using data: %s" % data)
        return self.anycast_info_by_cidr(data['cidr'])

    def anycast_info_by_cidr(self, cidr):
        return self._generic_info_(
            "anycast", models.Anycast, {'cidr': cidr.replace('_','/')}
        )

    def subnet_info(self, id):
        return self._generic_info_("subnet", models.Subnet, {'id': id})

    def anycast_info(self, id):
        return self._generic_info_("anycast", models.Anycast, {'id': id})

    def subnet_info_by_cidr(self, cidr):
        return self._generic_info_(
            "subnet", models.Subnet, {'cidr': cidr.replace('_','/')}
        )

    def subnet_update(self, *args, **kwargs):
        raise FeatureNotAvailable()

    @post_run
    def subnet_delete(self, id):
        subnet = session.query(models.Subnet).get(id)
        vlan = subnet.vlan
        ret = self._generic_delete_("subnet", models.Subnet, {'id': id})
        #self._enqueue_dhcp_entries_(vlan, 'update')
        return ret

    def anycast_delete(self, id):
        return self._generic_delete_("anycast", models.Anycast, {'id': id})

    def ip_list(self):
        return self._generic_list_("ips", models.Ip)

    def ip_list_by_subnet(self, subnet_id):
        return self._generic_list_by_something_(
            "ip info by subnet", models.Ip, {'subnet_id': subnet_id}
        )

    def anycastip_list_by_anycast(self, anycast_id):
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
        if not subnet:
            raise OperationNotPermited('Ip', "subnet_id %s doesnt exist" % subnet_id)
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
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "subnet_id %s doesnt exist" % subnet_id
            elif msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['ip']
            else:
                forbidden_msg = "Unknown error"
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
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "anycast_id %s doesnt exist" % anycast_id
            elif msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['ip']
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Anycastip', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        return self.anycastip_info_by_ip(data['ip'])

    def ip_info(self, id):
        return self._generic_info_("ip", models.Ip, {'id': id})

    def anycastip_info(self, id):
        return self._generic_info_("ip anycast", models.Anycastip, {'id': id})

    def vlan_info_by_ip(self, ip):
        query = {'ip': ip}
        ss = session.query(models.Ip).filter_by(**query).first()
        if not ss:
            raise EntityNotFound('Ip', query)

        return ss.subnet.vlan.to_dict()

    def ip_info_by_ip(self, ip):
        return self._generic_info_("ip", models.Ip, {'ip': ip})

    def anycastip_info_by_ip(self, ip):
        return self._generic_info_(
            "ip anycast", models.Anycastip, {'ip': ip}
        )

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def ip_delete(self, id):
        return self._generic_delete_("ip", models.Ip, {'id': id})

    def anycastip_delete(self, id):
        return self._generic_delete_("ip anycast", models.Anycastip, {'id': id})

    def policy_list(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def policy_create(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def policy_info(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def policy_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def policy_delete(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def interface_list(self):
        return self._generic_list_("interfaces", models.Interface)

    def interface_create(self, data):
        logger.debug("Creating interface using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(models.Interface(id=data['mac'], hostname=data['hostname']))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1:
                forbidden_msg = "%s already exists" % data['mac']
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Interface', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)

        return self.interface_info_by_mac(data['mac'])

    def interface_delete(self, data):
        return self._generic_delete_("interface", models.Interface, {'id': data})

    def interface_info(self, mac):
        return self.interface_info_by_mac(mac)

    def interface_info_by_mac(self, mac):
        return self._generic_info_("interface", models.Interface, {'id': mac})

    @post_run
    def interface_add_ip(self, interface_id, data):
        logger.debug("Adding IP to interface using data: %s" % data)

        interface = session.query(models.Interface).get(interface_id)
        ip = session.query(models.Ip).filter_by(**data).first()

        if not ip:
            raise EntityNotFound('Ip', data)
        elif not interface:
            raise EntityNotFound('Interface', interface_id)

        session.begin(subtransactions=True)
        try:
            interface.ips.add(ip)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        #self._enqueue_dhcp_entries_(ip.subnet.vlan, 'update')
        _data = interface.to_dict()
        logger.debug("Successful adding IP to interface status: %s" % _data)

        return _data

    @post_run
    def interface_remove_ip(self, interface_id, ip_id):
        interface = session.query(models.Interface).get(interface_id)
        if not self.valid_uuid(ip_id):
            new_ip_id = self.ip_info_by_ip(ip_id)
            if not self.valid_uuid(new_ip_id.get("id")):
                raise EntityNotFound('Ip', ip_id)
            ip_id = new_ip_id.get("id")

        ip = session.query(models.Ip).get(ip_id)

        if not ip:
            raise EntityNotFound('Ip', ip_id)
        elif not interface:
            raise EntityNotFound('Interface', interface_id)

        if ip in interface.ips:
            session.begin(subtransactions=True)
            try:
                interface.ips.remove(ip)
                session.commit()
            except Exception, e:
                session.rollback()
                raise Exception(e)
            _data = interface.to_dict()
            logger.debug("Successful removing IP to interface status: %s" % _data)
        else:
            _data = interface.to_dict()
        #self._enqueue_dhcp_entries_(ip.subnet.vlan, 'update')
        return _data

class Net(SimpleNet):
    pass
