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

from simplenet.common import event
from simplenet.db import models, db_utils
from simplenet.exceptions import EntityNotFound, OperationNotPermited
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError

from kombu import Exchange, BrokerConnection
from kombu.common import maybe_declare
from kombu.pools import producers

import os
import json
myname = os.uname()[1]

LOG = logging.getLogger(__name__)
session = db_utils.get_database_session()

class Net(SimpleNet):

    def _enqueue_rules_(self, owner_type, owner_id):
        policy_list = []
        _get_data = getattr(self, "_get_data_%s_" % owner_type)
        _data = _get_data(owner_id)

        print json.dumps(_data, sort_keys=True, indent=4)

        if (owner_type != 'zone') and ('vlan_id' in _data):
            devices = self.device_list_by_vlan(_data['vlan_id'])
        elif ('anycast_id' in _data):
            devices = self.device_list_by_anycast(_data['anycast_id'])
        else:
            devices = self.device_list_by_zone(_data['zone_id'])

        for device in devices:
            print 'Loop start'
            zone_id = device['zone_id']
            dev_id = device['device_id'] if (owner_type != 'zone') else device['id']
            if not 'name' in device:
                device['name'] = device['device']

            print "Modified Device:", device['name']
            policy_list = policy_list + self.policy_list_by_owner('zone', zone_id)
            _data.update({'policy': self.policy_list_by_owner('zone', zone_id)})
            for vlan in self.vlan_list_by_device(dev_id): # Cascade thru the vlans of the device
                print "Modified VLANs:", vlan['vlan_id']
                _get_data = getattr(self, "_get_data_%s_" % 'vlan')
                _data.update(_get_data(vlan['vlan_id']))
                policy_list = policy_list + self.policy_list_by_owner('vlan', vlan['vlan_id'])
                for subnet in self.subnet_list_by_vlan(vlan['vlan_id']): # Cascade thru the subnets of the vlan
                    print "Modified subnet:", subnet['id']
                    _get_data = getattr(self, "_get_data_%s_" % 'subnet')
                    _data.update(_get_data(subnet['id']))
                    policy_list = policy_list + self.policy_list_by_owner('subnet', subnet['id'])
                    for ip in self.ip_list_by_subnet(subnet['id']): # Cascade thru the IPs of the subnet
                        print "Modified IP:",  ip['id']
                        _get_data = getattr(self, "_get_data_%s_" % 'ip')
                        _data.update(_get_data(ip['id']))
                        policy_list = policy_list + self.policy_list_by_owner('ip', ip['id'])

            print 'Start Anycast'
            if ('anycast_id' in _data):
                for anycast in self.anycast_list_by_device(dev_id): # Cascade thru the anycasts of the device
                    print "Modified Anycast:", _data['anycast']
                    _get_data = getattr(self, "_get_data_%s_" % 'anycast')
                    _data.update(_get_data(_data['anycast_id']))
                    policy_list = policy_list + self.policy_list_by_owner('anycast', _data['anycast_id'])
                    for ip in self.ip_list_by_anycast(_data['anycast_id']): # Cascade thru the IPs of the anycast subnet
                        print "Modified IP Anycast:",  ip['id']
                        _get_data = getattr(self, "_get_data_%s_" % 'ipanycast')
                        _data.update(_get_data(ip['id']))
                        policy_list = policy_list + self.policy_list_by_owner('Ipanycast', ip['id'])

            print 'End Anycast'
            _data.update({'policy': policy_list})

            #print json.dumps(_data, sort_keys=True, indent=4)

            if policy_list:
                event.EventManager().raise_event(device['name'], _data)

            print 'Loop end'

    def policy_list(self, owner_type):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).all()
        policies = []
        for policy in ss:
            policies.append(
                policy.to_dict()
            )
        return policies

    def policy_create(self, owner_type, owner_id, data):
        data.update({'owner_id': owner_id})
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        policy = _model(**data)
        session.begin(subtransactions=True)
        try:
            session.add(policy)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        self._enqueue_rules_(owner_type, owner_id)
        return self.policy_info(owner_type, policy.id)

    def policy_info(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).get(id)
        if not ss:
            raise EntityNotFound('%sPolicy' % owner_type.capitalize(), id)
        return ss.to_dict()

    def policy_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_delete(self, owner_type, id):
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

        self._enqueue_rules_(owner_type, owner_id)
        return True

    def policy_list_by_owner(self, owner_type, id):
        _model = getattr(models, "%sPolicy" % owner_type.capitalize())
        ss = session.query(_model).filter_by(owner_id=id).all()
        policies = []
        for policy in ss:
            policies.append(
                policy.to_dict()
            )
        return policies
