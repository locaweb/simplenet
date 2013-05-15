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
from simplenet.common.config import config, get_logger
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotImplemented, EntityNotFound,
    OperationNotPermited, FeatureNotAvailable
)
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError

logger = get_logger()
session = db_utils.get_database_session()

class Net(SimpleNet):

    def dhcp_create(self, data):
        logger.debug("Creating device(DHCP) using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(models.Dhcp(name=data['name']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Dhcp', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created device(DHCP) using data: %s" % data)

        return self.dhcp_info_by_name(data['name'])

    def dhcp_list(self):
        return self._generic_list_("dhcps", models.Dhcp)

    def dhcp_add_vlan(self, dhcp_id, data):
        logger.debug("Adding vlan to device: %s using data: %s" %
            (dhcp_id, data)
        )
        dhcp = session.query(models.Dhcp).get(dhcp_id)
        vlan = session.query(models.Vlan).get(data['vlan_id'])

        session.expire_all()
        session.begin(subtransactions=True)
        try:
            relationship = models.Vlans_to_Dhcp()
            relationship.vlan = vlan
            dhcp.vlans_to_dhcps.append(relationship)
            session.commit()
            session.flush()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        _data = dhcp.to_dict()
        logger.debug("Successful adding vlan to device:"
            " %s device status: %s" % (dhcp_id, _data)
        )
        return _data

    def dhcp_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "dhcps by vlan", models.Vlans_to_Dhcp, {'vlan_id': vlan_id}
        )

    def dhcp_remove_vlan(self, dhcp_id, vlan_id):
        return self._generic_delete_(
            "vlan from dhcps", models.Vlans_to_Dhcp,
            {'vlan_id': vlan_id, 'dhcp_id': dhcp_id}
        )

    def dhcp_info(self, id):
        return self._generic_info_("dhcp", models.Dhcp, {'id': id})

    def dhcp_info_by_name(self, name):
        return self._generic_info_(
            "dhcp", models.Dhcp, {'name': name}
        )

    def dhcp_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def dhcp_delete(self, id):
        return self._generic_delete_("dhcp", models.Dhcp, {'id': id})

    def _enqueue_dhcp_entries_(self, dhcp_id):
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
        else:
            logger.debug("Getting devices by zone: %s" % _data['zone_id'])
            devices = self.firewall_list_by_zone(_data['zone_id'])

        for device in devices:
            logger.debug("Getting data from device: %s" % device['id'])
            zone_id = device['zone_id']
            dev_id = device['device_id'] if (owner_type != 'zone') else device['id']

            policy_list = policy_list + self.policy_list_by_owner('zone', zone_id)
            _data.update({'policy': self.policy_list_by_owner('zone', zone_id)})
            for vlan in self.vlan_list_by_firewall(dev_id): # Cascade thru the vlans of the device
                logger.debug("Getting policy data from vlan: %s" % vlan)
                policy_list = policy_list + self.policy_list_by_owner('vlan', vlan['vlan_id'])
                for subnet in self.subnet_list_by_vlan(vlan['vlan_id']): # Cascade thru the subnets of the vlan
                    logger.debug("Getting policy data from subnet: %s" % subnet)
                    policy_list = policy_list + self.policy_list_by_owner('subnet', subnet['id'])
                    logger.debug("maldito %s" % json.dumps(subnet['id']))
                    logger.debug("maldito %s" % json.dumps(self.ip_list_by_subnet(subnet['id'])))
                    for ip in self.ip_list_by_subnet(subnet['id']): # Cascade thru the IPs of the subnet
                        logger.debug("maldito %s" % json.dumps(ip.keys()))
                        logger.debug("Getting policy data from ip: %s" % ip)
                        policy_list = policy_list + self.policy_list_by_owner('ip', ip['id'])

            for anycast in self.anycast_list_by_firewall(dev_id): # Cascade thru the anycasts of the device
                logger.debug("Getting policy data from anycast %s" % anycast)
                policy_list = policy_list + self.policy_list_by_owner('anycast', anycast['anycast_id'])
                for anycastip in self.anycastip_list_by_anycast(anycast['anycast_id']): # Cascade thru the IPs of the anycast subnet
                    logger.debug("Getting policy data from anycasip %s" % anycastip)
                    policy_list = policy_list + self.policy_list_by_owner('anycastip', anycastip['id'])

            _data.update({'policy': policy_list})
            logger.debug("Received rules: %s from %s with id %s and device %s" % (
                _data, owner_type, id, device['name'])
            )
            if policy_list:
                event.EventManager().raise_event(device['name'], _data)

