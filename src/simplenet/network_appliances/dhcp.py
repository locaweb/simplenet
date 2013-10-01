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
from simplenet.db import models, db_utils
from simplenet.exceptions import (
    FeatureNotAvailable, OperationNotPermited
)
from simplenet.network_appliances.base import SimpleNet

from sqlalchemy.exc import IntegrityError, FlushError

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

    def dhcp_rebuild_queues(self, vlan_id):
        logger.debug("Rebuilding queue for %s" %
            (vlan_id)
        )
        vlan = session.query(models.Vlan).get(vlan_id)
        self._enqueue_dhcp_(vlan, '', 'rebuild_queues')

    def dhcp_add_vlan(self, dhcp_id, vlan_id):
        logger.debug("Adding vlan to device: %s using data: %s" %
            (dhcp_id, vlan_id)
        )
        dhcp = session.query(models.Dhcp).get(dhcp_id)
        vlan = session.query(models.Vlan).get(vlan_id)

        session.expire_all()
        session.begin(subtransactions=True)
        try:
            relationship = models.Vlans_to_Dhcp()
            relationship.vlan = vlan
            dhcp.vlans_to_dhcps.append(relationship)
            session.commit()
            session.flush()
        except FlushError:
            session.rollback()
            raise OperationNotPermited('dhcp_add_vlan', 'Entry already exist')
        self._enqueue_dhcp_(vlan, dhcp, 'new')
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
        dhcp = session.query(models.Dhcp).get(dhcp_id)
        vlan = session.query(models.Vlan).get(vlan_id)
        ret = self._generic_delete_(
            "vlan from dhcps", models.Vlans_to_Dhcp,
            {'vlan_id': vlan_id, 'dhcp_id': dhcp_id}
        )
        self._enqueue_dhcp_(vlan, dhcp, 'remove')
        return ret

    def dhcp_info(self, id):
        return self._generic_info_("dhcp", models.Dhcp, {'id': id})

    def dhcp_info_by_name(self, name):
        return self._generic_info_(
            "dhcp", models.Dhcp, {'name': name}
        )

    def dhcp_update(self, *args, **kawrgs):
        raise FeatureNotAvailable()

    def dhcp_delete(self, id):
        return self._generic_delete_("dhcp", models.Dhcp, {'id': id})

    def _enqueue_dhcp_(self, vlan, dhcp, action):
        _data = {}
        entries = {}
        _data['action'] = action
        ss = [x.vlan.subnet for x in session.query(models.Vlans_to_Dhcp).filter_by(**{'dhcp_id': dhcp.id}).all()]
        subnets = []
        if ss:
            [subnets.extend(x) for x in ss]
        for subnet in subnets:
            network = subnet.network()
            _data[network] = {}
            _data[network]['gateway'] = subnet.gateway()
            for ip in self.ip_list_by_subnet(subnet.id):
                entries.update({ip['ip']: [ip['interface_id'], ip['hostname'] or "defaulthostname"]})

        if action == 'rebuild_queues':
            for dhcp in self.dhcp_list_by_vlan(vlan.id):
                event.EventManager().raise_fanout_event(vlan.name, 'dhcp:'+dhcp['name'], _data)
        else:
            event.EventManager().raise_fanout_event(vlan.name, 'dhcp:'+dhcp.name, _data)
            event.EventManager().raise_event('dhcp:'+dhcp.name, _data)

    def _enqueue_dhcp_entries_(self, vlan, action):
        _data = {}
        entries = {}
        subnets = vlan.subnet
        for subnet in subnets:
            network = subnet.network()
            _data[network] = {}
            _data[network]['gateway'] = subnet.gateway()
            for ip in self.ip_list_by_subnet(subnet.id):
                entries.update({ip['ip']: [ip['interface_id'], ip['hostname'] or "defaulthostname"]})

        event.EventManager().raise_fanout_event(vlan.name, '', {'network': _data, 'entries': entries, 'action': action})