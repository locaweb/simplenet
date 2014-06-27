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
from simplenet.db.models import new_model, Firewall, Anycast, Anycasts_to_Firewall
from simplenet.db import db_utils
from simplenet.exceptions import (
    FeatureNotAvailable, EntityNotFound,
    OperationNotPermited, DuplicatedEntryError
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

    def firewall_enable(self, data):
        session.begin()
        try:
            firewall = session.query(Firewall).filter_by(**data).first()
            firewall.enable()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.info("Firewall %s enabled" % firewall.name)
        return firewall.to_dict()

    def firewall_disable(self, data):
        session.begin()
        try:
            firewall = session.query(Firewall).filter_by(**data).first()
            firewall.disable()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.info("Firewall %s disabled" % firewall.name)
        return firewall.to_dict()

    def firewall_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(Firewall(name=data['name'], zone_id=data['zone_id'],
                                        mac=data['mac'], status=True))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "zone_id %s doesnt exist" % zone_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Firewall', "%s already exists" % data['name'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Firewall', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created device using data: %s" % data)

        return self.firewall_info_by_name(data['name'])

    def firewall_list(self):
        return self._generic_list_("Firewall")

    def firewall_add_anycast(self, firewall_id, data):
        logger.debug("Adding vlan to anycast: %s using data: %s" %
            (firewall_id, data)
        )
        firewall_id = self.retrieve_valid_uuid(firewall_id, self.firewall_info_by_name, "id")

        firewall = session.query(Firewall).get(firewall_id)
        anycast = session.query(Anycast).get(data['anycast_id'])

        session.begin(subtransactions=True)
        try:
            relationship = Anycasts_to_Firewall()
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
            "Vlans_to_Firewall", {'vlan_id': vlan_id}
        )

    def firewall_list_by_anycast(self, anycast_id):
        return self._generic_list_by_something_(
            "Anycasts_to_Firewall",
            {'anycast_id': anycast_id}
        )

    def firewall_remove_anycast(self, firewall_id, anycast_id):
        firewall_id = self.retrieve_valid_uuid(firewall_id, self.firewall_info_by_name, "id")

        return self._generic_delete_(
            "Anycasts_to_Firewall",
            {'anycast_id': anycast_id, 'firewall_id': firewall_id}
        )

    def firewall_info(self, id):
        return self._generic_info_("Firewall", {'id': id})

    def firewall_info_by_name(self, name):
        return self._generic_info_(
            "Firewall", {'name': name}
        )

    def firewall_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def firewall_delete(self, id):
        return self._generic_delete_("Firewall", {'id': id})

    def firewall_sync(self, data):
        _data = {}
        device = None
        _data['modified'] = None

        if data.get("name"):
            device = self.firewall_info_by_name(data.get("name"))
        elif data.get("id"):
            device = self.firewall_info(data.get("id"))
        else:
            raise EntityNotFound("Firewall", "Missing id or name")

        if device is None:
            raise EntityNotFound("Firewall", "not found with %s" % data)

        self._enqueue_device_rules_(_data, [device], "FW Reload")

        return device

    def _enqueue_rules_(self, owner_type, owner_id, mod):
        logger.debug("Getting rules from %s with id %s" % (owner_type, owner_id))
        policy_list = []
        _get_data = getattr(self, "_get_data_%s_" % owner_type)
        zone_id = _get_data(owner_id).get('zone_id')
        _data = {}
        #_data = _get_data(owner_id)
        _data['modified'] = mod

        logger.debug("Getting devices by zone: %s" % zone_id)
        devices = self.firewall_list_by_zone(zone_id)

        self._enqueue_device_rules_(_data, devices, owner_type)

    def _enqueue_device_rules_(self, data, devices, owner_type):
        policy_list = []
        cache = {}
        try:
            devices = devices.split()
        except AttributeError:
            pass

        for device in devices:
            if not device.get("status"):
                logger.info("Device %s ignored, status disabled" % device.get("name"))
                continue
            logger.debug("Getting data from device: %s" % device['id'])
            owners_ids = []
            zone_id = device['zone_id']

            if cache.get(zone_id):
                logger.info("Sending cached event to %s" % device['name'])
                event.EventManager().raise_event(device['name'], cache.get(zone_id))
            else:
                _data = data
                _data.update(self._get_data_zone_(zone_id))
                _data['anycasts'] = []
                _data['anycastips'] = []
                dev_id = device.get('device_id') or device.get('id')

                logger.debug("Getting policy data from zone %s" % zone_id)
                policy_list += self.policy_list_by_owner('zone', zone_id)
                for vlan in self.vlan_list_by_zone(zone_id): # Cascade thru the vlans of the device
                    owners_ids.append(vlan['id'])
                    for subnet in self.subnet_list_by_vlan(vlan['id']): # Cascade thru the subnets of the vlan
                        owners_ids.append(subnet['id'])
                        for ip in self.ip_list_by_subnet(subnet['id']): # Cascade thru the IPs of the subnet
                            owners_ids.append(ip['id'])

                for anycast in self.anycast_list_by_firewall(dev_id): # Cascade thru the anycasts of the device
                    owners_ids.append(anycast['anycast_id'])
                    _data['anycasts'].append(anycast)
                    for anycastip in self.anycastip_list_by_anycast(anycast['anycast_id']): # Cascade thru the IPs of the anycast subnet
                        _data['anycastips'].append(anycastip)
                        owners_ids.append(anycastip['id'])

                logger.debug("Getting policy data")
                policy_list += self.policy_list_by_owners(owners_ids)

                _data.update({'policy': policy_list})
                logger.debug("Received rules: %s from %s with id %s and device %s" % (
                    _data, owner_type, id, device['name'])
                )
                if policy_list:
                    logger.info("Sending event to %s" % device['name'])
                    cache[zone_id] = _data
                    event.EventManager().raise_event(device['name'], _data)

    def policy_list(self, owner_type):
        return self._generic_list_("%sPolicy" % owner_type.capitalize())

    def policy_create(self, owner_type, owner_id, data):
        logger.debug("Creating rule on %s: %s using data: %s" %
            (owner_type, owner_id, data)
        )
        data.update({'owner_id': owner_id})
        _model, _ = new_model("%sPolicy" % owner_type.capitalize())
        policy = _model(**data)

        session.begin(subtransactions=True)
        try:
            session.add(policy)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise DuplicatedEntryError('Firewall', "%s already exists" % data)
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Created rule %s on %s: %s using data: %s" %
            (policy.id, owner_type, owner_id, data)
        )
        pol = self.policy_info(owner_type, policy.id)

        try:
            self._enqueue_rules_(owner_type, owner_id, pol)
        except Exception, e:
            raise
            logger.error("Policy created but firewall event failed %s" % str(e))

        return pol

    def policy_info(self, owner_type, id):
        return self._generic_info_("%sPolicy" % owner_type.capitalize(), {'id': id})

    def policy_update(self, *args, **kwargs):
        raise FeatureNotAvailable()

    def policy_delete(self, owner_type, id):
        logger.debug("Deleting policy %s" % id)
        _model, _ = new_model("%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).get(id)
        if not ss:
            return True
        modified = ss.to_dict()
        owner_id = ss.owner_id
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        logger.debug("Successful deletion of policy %s" % id)
        self._enqueue_rules_(owner_type, owner_id, modified)
        return True

    def policy_delete_by_owner(self, owner_type, id):
        _model, _ = new_model("%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).filter_by(**{'owner_id': id}).all()
        if ss:
            try:
                for s in ss:
                    session.delete(s)
                session.commit()
            except Exception, e:
                session.rollback()
                raise Exception(e)
            self._enqueue_rules_(owner_type, id, {})

    def policy_list_by_owner(self, owner_type, id):
        return self._generic_list_by_something_(
            "%sPolicy" % owner_type.capitalize(), {'owner_id': id}
        )

    def policy_list_by_owners(self, ids):
        if ids == []:
            return []
        model, _ = new_model("Policy")
        logger.debug("Getting policies by ids %s" % (ids))
        ss = session.query(model).filter(model.owner_id.in_(ids)).all()
        _values = []
        for _value in ss:
            _values.append(
                _value.to_dict()
            )
        logger.debug("Received: %s from [%s]" % (_values, ids))
        return _values
