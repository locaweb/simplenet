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

import json
from simplenet.common import event
from simplenet.common.config import get_logger
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotAvailable, EntityNotFound,
    OperationNotPermited
)
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()

class Net(SimpleNet):

    def _get_data_firewall_(self, id):
        logger.debug("Getting device data %s" % id)
        firewall = self.firewall_info(id)
        zone = self.zone_info(firewall['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received device: %s zone: %s "
            "datacenter: %s from [%s]" %
            (firewall, zone, datacenter, id)
        )
        return {
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
        }

    def firewall_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(models.Firewall(name=data['name'], zone_id=data['zone_id'],
                                        mac=data['mac']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Firewall', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created device using data: %s" % data)

        return self.firewall_info_by_name(data['name'])

    def firewall_list(self):
        return self._generic_list_("firewalls", models.Firewall)

    def firewall_add_vlan(self, firewall_id, data):
        logger.debug("Adding vlan to device: %s using data: %s" %
            (firewall_id, data)
        )
        firewall = session.query(models.Firewall).get(firewall_id)
        vlan = session.query(models.Vlan).get(data['vlan_id'])

        if firewall.zone_id != vlan.zone_id:
            raise OperationNotPermited(
                'Firewall', 'Firewall and Vlan must be from the same zone'
            )

        session.expire_all()
        session.begin(subtransactions=True)
        try:
            relationship = models.Vlans_to_Firewall()
            relationship.vlan = vlan
            firewall.vlans_to_firewalls.append(relationship)
            session.commit()
            session.flush()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        _data = firewall.to_dict()
        logger.debug("Successful adding vlan to device:"
            " %s device status: %s" % (firewall_id, _data)
        )
        return _data

    def firewall_add_anycast(self, firewall_id, data):
        logger.debug("Adding vlan to anycast: %s using data: %s" %
            (firewall_id, data)
        )
        firewall = session.query(models.Firewall).get(firewall_id)
        anycast = session.query(models.Anycast).get(data['anycast_id'])

        session.begin(subtransactions=True)
        try:
            relationship = models.Anycasts_to_Firewall()
            relationship.anycast = anycast
            firewall.anycasts_to_firewalls.append(relationship)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        _data = firewall.to_dict()
        logger.debug("Successful adding vlan to anycast: %s device status: %s" %
            (firewall_id, _data)
        )
        return _data

    def firewall_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "firewalls by vlan", models.Vlans_to_Firewall, {'vlan_id': vlan_id}
        )

    def firewall_list_by_anycast(self, anycast_id):
        return self._generic_list_by_something_(
            "firewalls by anycast", models.Anycasts_to_Firewall,
            {'anycast_id': anycast_id}
        )

    def firewall_list_by_zone(self, zone_id):
        return self._generic_list_by_something_(
            "firewalls by zone", models.Firewall, {'zone_id': zone_id}
        )

    def firewall_remove_vlan(self, firewall_id, vlan_id):
        return self._generic_delete_(
            "vlan from firewalls", models.Vlans_to_Firewall,
            {'vlan_id': vlan_id, 'firewall_id': firewall_id}
        )

    def firewall_remove_anycast(self, firewall_id, anycast_id):
        return self._generic_delete_(
            "anycast from firewall", models.Anycasts_to_Firewall,
            {'anycast_id': anycast_id, 'firewall_id': firewall_id}
        )

    def firewall_info(self, id):
        return self._generic_info_("firewall", models.Firewall, {'id': id})

    def firewall_info_by_name(self, name):
        return self._generic_info_(
            "firewall", models.Firewall, {'name': name}
        )

    def firewall_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def firewall_delete(self, id):
        return self._generic_delete_("firewall", models.Firewall, {'id': id})

    def _enqueue_rules_(self, owner_type, owner_id):
        logger.debug("Getting rules from %s with id %s" % (owner_type, owner_id))
        policy_list = []
        _get_data = getattr(self, "_get_data_%s_" % owner_type)
        _data = _get_data(owner_id)

        if (owner_type != 'zone') and ('vlan_id' in _data):
            logger.debug("Getting devices by vlan: %s" % _data['vlan_id'])
            devices = self.firewall_list_by_vlan(_data['vlan_id'])
        elif ('anycast_id' in _data):
            logger.debug("Getting devices by anycast: %s" % _data['anycast_id'])
            devices = self.firewall_list_by_anycast(_data['anycast_id'])
        elif (owner_type == 'datacenter'):
            logger.debug("Getting devices by datacenter: %s" % _data['datacenter'])
            for x in _data['zones']:
                [self._enqueue_device_rules_(_data, y, owner_type) for y in self.firewall_list_by_zone(x['id'])]
            return
        else:
            logger.debug("Getting devices by zone: %s" % _data['zone_id'])
            devices = self.firewall_list_by_zone(_data['zone_id'])

        self._enqueue_device_rules_(_data, devices, owner_type)

    def _enqueue_device_rules_(self, _data, devices, owner_type):
        policy_list = []
        try:
            devices = devices.split()
        except AttributeError:
            pass

        for device in devices:
            logger.debug("Getting data from device: %s" % device['id'])
            vlans = []
            subnets = []
            ips = []
            anycasts = []
            anycastips = []
            zone_id = device['zone_id']
            _data.update(self._get_data_zone_(zone_id))
            dev_id = device.get('device_id') or device.get('id')

            logger.debug("Getting policy data from zone %s" % zone_id)
            policy_list += self.policy_list_by_owner('zone', zone_id)
            for vlan in self.vlan_list_by_firewall(dev_id): # Cascade thru the vlans of the device
                vlans.append(vlan['vlan_id'])
                for subnet in self.subnet_list_by_vlan(vlan['vlan_id']): # Cascade thru the subnets of the vlan
                    subnets.append(subnet['id'])
                    for ip in self.ip_list_by_subnet(subnet['id']): # Cascade thru the IPs of the subnet
                        ips.append(ip)

            for anycast in self.anycast_list_by_firewall(dev_id): # Cascade thru the anycasts of the device
                anycasts.append(anycast['anycast_id'])
                for anycastip in self.anycastip_list_by_anycast(anycast['anycast_id']): # Cascade thru the IPs of the anycast subnet
                    anycastips.append(ip['id'])

            logger.debug("Getting policy data from vlans: %s" % vlans)
            policy_list += self.policy_list_by_owners('vlan', vlans)
            logger.debug("Getting policy data from subnets: %s" % subnets)
            policy_list += self.policy_list_by_owners('subnet', subnets)
            logger.debug("Getting policy data from ips: %s" % [x['id'] for x in ips])
            policy_list += self.policy_list_by_owners('ip', [x['id'] for x in ips])

            logger.debug("Getting policy data from anycasts %s" % anycasts)
            policy_list = policy_list + self.policy_list_by_owners('anycast', anycasts)
            logger.debug("Getting policy data from anycasips %s" % anycastips)
            policy_list = policy_list + self.policy_list_by_owners('anycastip', anycastips)

            _data.update({'policy': policy_list})
            logger.debug("Received rules: %s from %s with id %s and device %s" % (
                _data, owner_type, id, device['name'])
            )
            if policy_list:
                event.EventManager().raise_event(device['name'], _data)

    def policy_list(self, owner_type):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_list_("%sPolicy" % owner_type.capitalize(), _model)

    def policy_create(self, owner_type, owner_id, data):
        logger.debug("Creating rule on %s: %s using data: %s" %
            (owner_type, owner_id, data)
        )
        data.update({'owner_id': owner_id})
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        policy = _model(**data)
        session.begin(subtransactions=True)
        try:
            session.add(policy)
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data
            raise OperationNotPermited('Firewall', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Created rule %s on %s: %s using data: %s" %
            (policy.id, owner_type, owner_id, data)
        )
        self._enqueue_rules_(owner_type, owner_id)
        return self.policy_info(owner_type, policy.id)

    def policy_info(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_info_("%sPolicy" % owner_type.capitalize(), _model, {'id': id})

    def policy_update(self, *args, **kwargs):
        raise FeatureNotAvailable()

    def policy_delete(self, owner_type, id):
        logger.debug("Deleting policy %s" % id)
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).get(id)
        if not ss:
            raise EntityNotFound('%sPolicy' % owner_type.capitalize(), id)
        owner_id = ss.owner_id
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Successful deletion of policy %s" % id)
        self._enqueue_rules_(owner_type, owner_id)
        return True

    def policy_list_by_owner(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        return self._generic_list_by_something_(
            "%sPolicy" % owner_type.capitalize(), _model, {'owner_id': id}
        )

    def policy_list_by_owners(self, owner_type, ids):
        if ids == []:
            return []
        _type = "%sPolicy" % owner_type.capitalize()
        model = getattr(models, _type)
        logger.debug("Getting %s by %s" % (_type, ids))
        ss = session.query(model).filter(model.owner_id.in_(ids)).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict()
            )
        logger.debug("Received %s: %s from [%s]" % (_type, _values, ids))
        return _values
