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
from simplenet.db.models import new_model, Router
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

    def _get_data_router_(self, id):
        logger.debug("Getting device data %s" % id)
        router = self.router_info(id)
        zone = self.zone_info(router['zone_id'])
        datacenter = self.datacenter_info(zone['datacenter_id'])
        logger.debug("Received device: %s zone: %s "
            "datacenter: %s from [%s]" %
            (router, zone, datacenter, id)
        )
        return {
            'zone': zone['name'],
            'zone_id': zone['id'],
            'datacenter': datacenter['name'],
            'datacenter_id': datacenter['id'],
        }

    def router_enable(self, data):
        session.begin()
        try:
            router = session.query(Router).filter_by(**data).first()
            router.enable()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.info("Router %s enabled" % router.name)
        return router.to_dict()

    def router_disable(self, data):
        session.begin()
        try:
            router = session.query(Router).filter_by(**data).first()
            router.disable()
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.info("Router %s disabled" % router.name)
        return router.to_dict()

    def router_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(Router(name=data['name'], zone_id=data['zone_id'],
                                        mac=data['mac'], status=True))
            session.commit()
        except IntegrityError, e:
            session.rollback()
            msg = e.message
            if msg.find("foreign key constraint failed") != -1:
                forbidden_msg = "zone_id %s doesnt exist" % zone_id
            elif msg.find("is not unique") != -1 or msg.find("Duplicate entry") != -1:
                raise DuplicatedEntryError('Router', "%s already exists" % data['name'])
            else:
                forbidden_msg = "Unknown error"
            raise OperationNotPermited('Router', forbidden_msg)
        except Exception, e:
            session.rollback()
            raise Exception(e)
        logger.debug("Created device using data: %s" % data)

        return self.router_info_by_name(data['name'])

    def router_list(self):
        return self._generic_list_("Router")

    def router_list_by_vlan(self, vlan_id):
        return self._generic_list_by_something_(
            "Vlans_to_Router", {'vlan_id': vlan_id}
        )

    def router_info(self, id):
        return self._generic_info_("Router", {'id': id})

    def router_info_by_name(self, name):
        return self._generic_info_(
            "Router", {'name': name}
        )

    def router_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def router_delete(self, id):
        return self._generic_delete_("Router", {'id': id})
