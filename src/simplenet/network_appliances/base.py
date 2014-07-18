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
from simplenet.db.models import (
        new_model, Prober, Datacenter, Zone, Interface,
        Vlan, Subnet, Anycast, Ip, Anycastip
)
from simplenet.db import db_utils
from simplenet.exceptions import (
    FeatureNotAvailable, EntityNotFound,
    OperationNotPermited, DuplicatedEntryError,
    OperationFailed
)
from sqlalchemy.exc import IntegrityError


class SimpleNet(object):

    def __init__(self):
        self.logger = get_logger()
        self.session = db_utils.get_database_session()

    @staticmethod
    def retrieve_valid_uuid(data, _func, field):
        try:
            UUID(data)
        except ValueError:
            _dd = _func(data)
            if _dd:
                return _dd.get(field)
            else:
                return None

        return data

    def _generic_list_(self, model_name):
        model, name = new_model(model_name)
        self.logger.debug("Listing %s" % name)
        ss = self.session.query(model).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict(),
            )
        self.logger.debug("Received %s: %s" % (name, _values))
        return _values

    def _generic_delete_(self, model_name, value):
        model, name = new_model(model_name)
        self.logger.debug("Deleting %s from %s" % (value, name))
        ss = self.session.query(model).filter_by(**value).first()
        if ss is None:
            return
        self.session.begin(subtransactions=True)
        try:
            self.session.delete(ss)
            self.session.commit()
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Successful deletion of %s from %s" % (value, name))
        return True

    def _generic_info_(self, model_name, value):
        model, name = new_model(model_name)
        self.logger.debug("Getting %s info by %s" % (name, value))
        ss = self.session.query(model).filter_by(**value).first()
        if not ss:
            raise EntityNotFound(name, value)
        data = ss.to_dict()
        self.logger.debug("Received %s from [%s]" % (data, value))
        return data

    def _generic_list_by_something_(self, model_name, value):
        model, name = new_model(model_name)
        self.logger.debug("Getting %s by %s" % (name, value))
        ss = self.session.query(model).filter_by(**value).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict()
            )
        self.logger.debug("Received %s: %s from [%s]" % (name, _values, value))
        return _values

    def _get_data_ip_(self, id):
        self.logger.debug("Getting ip data %s" % id)
        ip = self.ip_info(id)
        subnet = self.subnet_info(ip['subnet_id'])
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        self.logger.debug("Received ip: %s vlan: %s zone: %s "
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
        self.logger.debug("Getting ip anycast data %s" % id)
        ip = self.anycastip_info(id)
        anycast = self.anycast_info(ip['anycast_id'])
        self.logger.debug("Received anycast: %s from [%s]" %
            (anycast, id)
        )
        return {
            'Anycastip': ip['ip'],
            'anycast': anycast['cidr'],
            'anycast_id': anycast['id'],
        }

    def _get_data_subnet_(self, id):
        self.logger.debug("Getting subnet data %s" % id)
        subnet = self.subnet_info(id)
        vlan = self.vlan_info(subnet['vlan_id'])
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        self.logger.debug("Received subnet: %s vlan: %s "
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
        self.logger.debug("Getting anycast data %s" % id)
        anycast = self.anycast_info(id)
        self.logger.debug("Received anycast: %s from [%s]" %
            (anycast, id)
        )
        return {
            'anycast_id': anycast['id'],
            'anycast': anycast['cidr'],
            'anycastips': self.anycastip_list_by_anycast(id)
        }

    def _get_data_vlan_(self, id):
        self.logger.debug("Getting vlan data %s" % id)
        vlan = self.vlan_info(id)
        zone = self.zone_info(vlan['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        self.logger.debug("Received vlan: %s zone: %s "
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
        self.logger.debug("Getting zone data %s" % id)
        zone = self.zone_info(id)
        datacenter = self.datacenter_info(zone['datacenter_id'])
        self.logger.debug("Received zone: %s datacenter: %s from [%s]" %
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
        self.logger.debug("Getting datacenter data %s" % id)
        datacenter = self.datacenter_info(id)
        self.logger.debug("Received datacenter: %s from [%s]" %
            (datacenter, id)
        )
        return {
            'datacenter': datacenter['name'],
            'zones': self.zone_list_by_datacenter(id),
        }

    def prober(self):
        self.logger.debug("Getting prober data")
        ss = self.session.query(Prober).all()
        self.logger.debug("Received prober: %s" % ss)
        return ss

    def firewall_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "Firewall", {'zone_id': zone_id}
        )

    def datacenter_list(self):
        return self._generic_list_("Datacenter")

    def datacenter_create(self, data):
        self.logger.debug("Creating datacenter using data: %s" % data)
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Datacenter(name=data['name']))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1  or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Datacenter', "%s already exists" % data['name'])
            else:
                raise OperationNotPermited('Datacenter', "Unknown error")
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created datacenter using data: %s" % data)
        return self.datacenter_info_by_name(data['name'])

    def datacenter_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def datacenter_info(self, id):
        return self._generic_info_("Datacenter", {'id': id})

    def datacenter_info_by_name(self, name):
        return self._generic_info_(
            "Datacenter", {'name': name}
        )

    def datacenter_delete(self, id):
        return self._generic_delete_("Datacenter", {'id': id})

    def zone_list(self):
        return self._generic_list_("Zone")

    def zone_list_by_datacenter(self, datacenter_id):
        return self._generic_list_by_something_(
            "Zone",
            {'datacenter_id': datacenter_id}
        )

    def zone_create(self, datacenter_id, data):
        self.logger.debug("Creating zone on datacenter: %s using data: %s" %
            (datacenter_id, data)
        )
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Zone(
                name=data['name'], datacenter_id=datacenter_id)
            )
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "datacenter_id %s doesnt exist" % datacenter_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Zone', "%s already exists" % data['name'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Zone', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created zone on datacenter: %s using data: %s" %
            (datacenter_id, data)
        )
        return self.zone_info_by_name(data['name'])

    def zone_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def zone_info(self, id):
        return self._generic_info_("Zone", {'id': id})

    def zone_info_by_name(self, name):
        return self._generic_info_(
            "Zone", {'name': name}
        )

    def zone_delete(self, id):
        return self._generic_delete_("Zone", {'id': id})

    def vlan_list(self):
        return self._generic_list_("Vlan")

    def vlan_list_by_firewall(self, firewall_id):
        return self._generic_list_by_something_(
            "Vlans_to_Firewall",
            {'firewall_id': firewall_id}
        )

    def vlan_list_by_dhcp(self, dhcp_id):
        return self._generic_list_by_something_(
            "Vlans_to_Dhcp",
            {'dhcp_id': dhcp_id}
        )

    def vlan_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "Vlan", {'zone_id': zone_id}
        )

    def vlan_create(self, zone_id, data):
        self.logger.debug("Creating vlan on zone: %s using data: %s" %
            (zone_id, data)
        )
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Vlan(name=data['name'], zone_id=zone_id,
                                    type=data['type'], vlan_num=data['vlan_num']))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "zone_id %s doesnt exist" % zone_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Vlan', "%s already exists" % data['name'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Vlan', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created vlan on zone: %s using data: %s" %
            (zone_id, data)
        )
        return self.vlan_info_by_name(data['name'])

    def vlan_info(self, id):
        return self._generic_info_("Vlan", {'id': id})

    def vlan_info_by_name(self, name):
        return self._generic_info_(
            "Vlan", {'name': name}
        )

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def vlan_delete(self, id):
        return self._generic_delete_("Vlan", {'id': id})

    def subnet_list(self):
        return self._generic_list_("Subnet")

    def anycast_list(self):
        return self._generic_list_("Anycast")

    def anycast_list_by_firewall(self, firewall_id):
        return self._generic_list_by_something_(
            "Anycasts_to_Firewall",
            {'firewall_id': firewall_id}
        )

    def subnet_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "Subnet",
            {'vlan_id': vlan_id}
        )

    @post_run
    def subnet_create(self, vlan_id, data):
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Subnet(cidr=data['cidr'], vlan_id=vlan_id))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "vlan_id %s doesnt exist" % vlan_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Subnet', "%s already exists" % data['cidr'])
            else:
                forbidden_msg = "Unknown error -- %s" % msg
            raise OperationNotPermited('Subnet', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        vlan = self.session.query(Vlan).get(vlan_id)
        #self._enqueue_dhcp_entries_(vlan, 'update')
        return self.subnet_info_by_cidr(data['cidr'])

    def anycast_create(self, data):
        self.logger.debug("Creating subnet using data: %s" % data)
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Anycast(cidr=data['cidr']))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Anycast', "%s already exists" % data['cidr'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Anycast', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created subnet using data: %s" % data)
        return self.anycast_info_by_cidr(data['cidr'])

    def anycast_info_by_cidr(self, cidr):
        return self._generic_info_(
            "Anycast", {'cidr': cidr.replace('_','/')}
        )

    def subnet_info(self, id):
        return self._generic_info_("Subnet", {'id': id})

    def anycast_info(self, id):
        return self._generic_info_("Anycast", {'id': id})

    def subnet_info_by_cidr(self, cidr):
        return self._generic_info_(
            "Subnet", {'cidr': cidr.replace('_','/')}
        )

    def subnet_update(self, *args, **kwargs):
        raise FeatureNotAvailable()

    @post_run
    def subnet_delete(self, id):
        subnet = self.session.query(Subnet).get(id)
        vlan = subnet.vlan
        ret = self._generic_delete_("Subnet", {'id': id})
        #self._enqueue_dhcp_entries_(vlan, 'update')
        return ret

    def anycast_delete(self, id):
        return self._generic_delete_("Anycast", {'id': id})

    def ip_list(self):
        return self._generic_list_("Ip")

    def ip_list_by_subnet(self, subnet_id):
        return self._generic_list_by_something_(
            "Ip", {'subnet_id': subnet_id}
        )

    def ip_list_by_id(self, ip_id):
        return self._generic_list_by_something_(
            "Ip", {'id': ip_id}
        )

    def anycastip_list_by_anycast(self, anycast_id):
        return self._generic_list_by_something_(
            "Anycastip", {'anycast_id': anycast_id}
        )

    def anycastip_list(self):
        return self._generic_list_("Anycastip")

    def ip_create(self, subnet_id, data):
        self.logger.debug("Creating ip on subnet: %s using data: %s" %
            (subnet_id, data)
        )
        subnet = self.session.query(Subnet).get(subnet_id)
        if not subnet:
            raise OperationNotPermited('Ip', "subnet_id %s doesnt exist" % subnet_id)
        if not subnet.contains(data['ip']):
            raise OperationNotPermited(
                'Ip', "%s address must be contained in %s" % (
                        data['ip'],
                        subnet.cidr
                )
            )
        self.session.begin(subtransactions=True)
        try:
            self.session.add(Ip(ip=data['ip'], subnet_id=subnet_id))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "subnet_id %s doesnt exist" % subnet_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Ip', "%s already exists" % data['ip'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Ip', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created ip on subnet: %s using data: %s" %
            (subnet_id, data)
        )
        return self.ip_info_by_ip(data['ip'])

    def anycastip_create(self, anycast_id, data):
        self.logger.debug("Creating ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        anycast = self.session.query(Anycast).get(anycast_id)
        if not anycast.contains(data['ip']):
            raise OperationNotPermited(
                'Ip', "%s address must be contained in %s" % (
                        data['ip'],
                        anycast.cidr
                )
            )
        self.session.begin(subtransactions=True)
        try:
            self.session.add(
                Anycastip(ip=data['ip'], anycast_id=anycast_id)
            )
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "anycast_id %s doesnt exist" % anycast_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Anycastip', "%s already exists" % data['ip'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Anycastip', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        self.logger.debug("Created ip on anycast: %s using data: %s" %
            (anycast_id, data)
        )
        return self.anycastip_info_by_ip(data['ip'])

    def ip_info(self, id):
        return self._generic_info_("Ip", {'id': id})

    def anycastip_info(self, id):
        return self._generic_info_("Anycastip", {'id': id})

    def vlan_info_by_ip(self, ip):
        query = {'ip': ip}
        ss = self.session.query(Ip).filter_by(**query).first()
        if not ss:
            raise EntityNotFound('Ip', query)

        return ss.subnet.vlan.to_dict()

    def ip_info_by_ip(self, ip):
        return self._generic_info_("Ip", {'ip': ip})

    def anycastip_info_by_ip(self, ip):
        return self._generic_info_(
            "Anycastip", {'ip': ip}
        )

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def ip_delete(self, id):
        import simplenet.network_appliances.firewall
        try:
            pol = simplenet.network_appliances.firewall.Net()
            pol.policy_delete_by_owner("ip", id)
            val = self._generic_delete_("Ip", {'id': id})
            return val
        except:
            self.logger.exception("Failed to delete IP")
            raise OperationFailed("Failed to delete IP")

    def anycastip_delete(self, id):
        return self._generic_delete_("Anycastip", {'id': id})

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
        return self._generic_list_("Interface")

    def interface_create(self, data):
        self.logger.debug("Creating interface using data: %s" % data)

        self.session.begin(subtransactions=True)
        try:
            self.session.add(Interface(id=data['mac'], hostname=data['hostname']))
            self.session.commit()
        except IntegrityError, e:
            self.session.rollback()
            msg = e.message
            if msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Interface', "%s already exists" % data['mac'])
            else:
                forbidden_msg = "Unknown error -- %s" % msg
            raise OperationNotPermited('Interface', forbidden_msg)
        except Exception, e:
            self.session.rollback()
            raise Exception(e)

        return self.interface_info_by_mac(data['mac'])

    def interface_delete(self, data):
        return self._generic_delete_("Interface", {'id': data})

    def interface_info(self, mac):
        return self.interface_info_by_mac(mac)

    def interface_info_by_mac(self, mac):
        return self._generic_info_("Interface", {'id': mac})

    def interface_add_vlan(self, interface_id, data):
        self.logger.debug("Adding VLAN to interface using data: %s" % data)

        interface = self.session.query(Interface).get(interface_id)
        if not interface:
            raise EntityNotFound('Interface', interface_id)

        if data == {} or type(data) != dict or (not data.get("id") and not data.get("name")):
            raise OperationNotPermited('Interface', "%s is not a valid input" % data)

        vlan = self.session.query(Vlan).filter_by(**data).first()
        if not vlan:
            raise EntityNotFound('Vlan', data)

        if vlan.type != "dedicated_vlan":
            raise OperationNotPermited('Vlan', "Cannot attach to interface a vlan with type %s" % vlan.type)

        self.session.begin(subtransactions=True)
        try:
            interface.vlan_id = vlan.id
            self.session.commit()
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        _data = interface.to_dict()
        self.logger.debug("Successful adding IP to interface status: %s" % _data)

        return _data

    def interface_remove_vlan(self, interface_id, vlan_id):
        interface = self.session.query(Interface).get(interface_id)
        vlan_id = self.retrieve_valid_uuid(vlan_id, self.vlan_info_by_name, "id")

        if not vlan_id:
            raise EntityNotFound('Vlan', vlan_id)
        elif not interface:
            raise EntityNotFound('Interface', interface_id)

        if interface.vlan_id == vlan_id:
            self.session.begin(subtransactions=True)
            try:
                interface.vlan_id = None
                self.session.commit()
            except Exception, e:
                self.session.rollback()
                raise Exception(e)
            _data = interface.to_dict()
            self.logger.debug("Successful removing IP to interface status: %s" % _data)
            return _data
        else:
            msg = "Vlan id doesnt match -- iface vlan (%s) received (%s)" % (interface.vlan_id, vlan_id)
            raise OperationNotPermited('Interface', msg)
            logger.error(msg)

    @post_run
    def interface_add_ip(self, interface_id, data):
        self.logger.debug("Adding IP to interface using data: %s" % data)

        interface = self.session.query(Interface).get(interface_id)
        if not interface:
            raise EntityNotFound('Interface', interface_id)

        if data == {} or type(data) != dict or (not data.get("id") and not data.get("ip")):
            raise OperationNotPermited('Interface', "%s is not a valid input" % data)

        ip = self.session.query(Ip).filter_by(**data).first()
        if not ip:
            raise EntityNotFound('Ip', data)

        self.session.begin(subtransactions=True)
        try:
            interface.ips.add(ip)
            self.session.commit()
        except Exception, e:
            self.session.rollback()
            raise Exception(e)
        #self._enqueue_dhcp_entries_(ip.subnet.vlan, 'update')
        _data = interface.to_dict()
        self.logger.debug("Successful adding IP to interface status: %s" % _data)

        return _data

    @post_run
    def interface_remove_ip(self, interface_id, ip_id):
        interface = self.session.query(Interface).get(interface_id)
        ip_id = self.retrieve_valid_uuid(ip_id, self.ip_info_by_ip, "id")

        ip = self.session.query(Ip).get(ip_id)

        if not ip:
            raise EntityNotFound('Ip', ip_id)
        elif not interface:
            raise EntityNotFound('Interface', interface_id)

        if ip in interface.ips:
            self.session.begin(subtransactions=True)
            try:
                interface.ips.remove(ip)
                self.session.commit()
            except Exception, e:
                self.session.rollback()
                raise Exception(e)
            _data = interface.to_dict()
            self.logger.debug("Successful removing IP to interface status: %s" % _data)
        else:
            _data = interface.to_dict()
        #self._enqueue_dhcp_entries_(ip.subnet.vlan, 'update')
        return _data

class Net(SimpleNet):
    pass
