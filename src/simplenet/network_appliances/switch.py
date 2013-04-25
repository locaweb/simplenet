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

    def switch_list(self):
        return self._generic_list_("switches", models.Switch)

    def switch_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(models.Switch(name=data['name'], mac=data['mac'],
                                    address=data['address'], model_type=data['model_type']))
            session.commit()
        except IntegrityError:
            session.rollback()
            forbidden_msg = "%s already exists" % data['name']
            raise OperationNotPermited('Switch', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created device using data: %s" % data)

        return self.switch_info_by_name(data['name'])


    def switch_info(self, id):
        return self._generic_info_("switch", models.Switch, {'id': id})


    def switch_info_by_name(self, name):
        return self._generic_info_(
            "switch", models.Switch, {'name': name}
        )

    def switch_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def switch_delete(self, id):
        return self._generic_delete_("switch", models.Switch, {'id': id})

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

    def firewall_remove_anycast(self, firewall_id, anycast_id):
        return self._generic_delete_(
            "anycast from firewall", models.Anycasts_to_Firewall,
            {'anycast_id': anycast_id, 'firewall_id': firewall_id}
        )

