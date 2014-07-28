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

from simplenet.common.event import EventManager
from simplenet.network_appliances.firewall import Net
from simplenet.common.config import config, get_logger

logger = get_logger()

def on_message(body, message):
    logger.info("Received ack for %s from %s" % (body.get("id"), body.get("device")))
    fw = Net()
    fw.policy_ack(body.get("id"))
    message.ack()

def on_flow_message(body, message):
    send_openflow = config.getboolean("event", "send_openflow")
    if (send_openflow and body['action'] == "get_flows"):
        logger.info("Flow request received %s" % body)
        fw = Net()
        rules = fw.policy_list_by_owners([body['owner']])
        for rule in rules:
            msg = {}
            msg['action'] = "add_openflow_fw"
            msg['firewallrule'] = rule
            msg['switch_name'] = body['switch_name']
            msg['id'] = body['mac']
            EventManager().raise_event(body['switch_name'].split(":")[0], msg)
        message.ack()
    else:
        logger.warning("Payload ignored %s" % body)
        message.ack()

def callback_run():
    EventManager().listen_event("simplenet", "firewall_ack", on_message)

def callback_run2():
    EventManager().listen_event("openflow", "openflow", on_flow_message)
