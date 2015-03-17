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

from simplenet.common import event
from simplenet.common.config import get_logger
from simplenet.db.models import Switch, Interface, Router
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
    def switch_list(self):
        return self._generic_list_("Switch")

    def switch_create(self, data):
        logger.debug("Creating device using data: %s" % data)

        session.begin(subtransactions=True)
        try:
            session.add(Switch(name=data['name'], mac=data['mac'],
                                    address=data['address'], model_type=data['model_type']))
            session.commit()
        except IntegrityError:
            session.rollback()
            raise DuplicatedEntryError('Switch', "%s already exists" % data['name'])
        except Exception, e:
            session.rollback()
            raise Exception(e)

        return self.switch_info_by_name(data['name'])

    def switch_info(self, id):
        return self._generic_info_("Switch", {'id': id})


    def switch_info_by_name(self, name):
        return self._generic_info_(
            "Switch", {'name': name}
        )

    def switch_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def switch_delete(self, id):
        return self._generic_delete_("Switch", {'id': id})

    def switch_add_interface(self, switch_id, data):
        logger.debug("Adding interface using data: %s" % data)

        interface = session.query(Interface).get(data['interface_id'])
        switch_id = self.retrieve_valid_uuid(switch_id, self.switch_info_by_name, "id")

        if not interface:
            raise EntityNotFound('Interface', data['interface_id'])

        if interface.switch_id:
            self.switch_remove_interface(interface.switch_id, data['interface_id'])

        session.begin(subtransactions=True)
        try:
            interface.switch_id = switch_id
            interface.name = data['int_name']
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)

        _data = interface.tree_dict()
        logger.debug("Successful adding Interface to Switch status: %s" % _data)
        _data['action'] = "plug"
        _data['ofport'] = data['ofport']
        zones = set()
        for ip in _data['ips']:
            zones.add(ip['subnet']['vlan']['zone_id'])

        _data['routers'] = []
        for zone in zones:
            for router in self.router_list_by_zone(zone):
                _data['routers'].append(router) if router.get("mac") is not None else None

        event.EventManager().raise_event(_data['switch_id']['name'].split(":")[0], _data)

        return _data

    def switch_remove_interface(self, switch_id, int_id):
        interface = session.query(Interface).get(int_id)
        if not interface:
            raise EntityNotFound('Interface', int_id)

        switch_id = self.retrieve_valid_uuid(switch_id, self.switch_info_by_name, "id")

        if not interface.switch_id:
            return
        elif interface.switch_id == switch_id:
            _data = interface.tree_dict()
            session.begin(subtransactions=True)
            try:
                interface.switch_id = None
                session.commit()
            except Exception, e:
                session.rollback()
                raise Exception(e)

            _data['action'] = "unplug"
            event.EventManager().raise_event(_data['switch_id']['name'].split(":")[0], _data)

            return _data
        else:
            raise Exception("Interface not plugged into the switch")
