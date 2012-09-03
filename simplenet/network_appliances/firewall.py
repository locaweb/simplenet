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

LOG = logging.getLogger(__name__)
session = db_utils.get_database_session()


class Net(SimpleNet):

    def _enqueue_rules_(self, owner_type, owner_id):
        policy_list = self.policy_list_by_owner(owner_type, owner_id)
        _get_data = getattr(self, "_get_data_%s_" % owner_type)
        _data = _get_data(owner_id)
        info_dependency = {
            'ip': ['datacenter', 'zone', 'vlan', 'subnet'],
            'subnet': ['datacenter', 'zone', 'vlan'],
            'vlan': ['datacenter', 'zone' ],
            'zone': ['datacenter']
        }

        for field in info_dependency[owner_type]:
            policy_list = policy_list + self.policy_list_by_owner(
                field, _data['%s_id' % field]
            )

        _data.update({'policy': policy_list})
        event.EventManager().raise_event("kanti", _data)

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
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
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
