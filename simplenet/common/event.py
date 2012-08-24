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
# @author: Thiago Morello, Locaweb.
# @author: Willian Molinari, Locaweb.
# @author: Juliano Martinez, Locaweb.

import logging
import socket

from kombu import BrokerConnection, Exchange, Queue

from simplenet.common.config import config, set_logger

LOG = logging.getLogger(__name__)


class EventManager(object):
    def __init__(self):
        # "amqp://guest:guest@localhost//"
        self.url = config.get("event", "broker")

    def raise_event(self, event_type, params, **kwargs):
        LOG.debug("Raising event %s with params: %s" % (event_type, params))
        with BrokerConnection(self.url) as conn:
            conn.ensure_connection()

            media_exchange = Exchange(
                    "simplenet",
                    type="direct",
                    durable=True)

            if 'route' in kwargs:
                routing_key = kwargs['route']
            else:
                queue = Queue(
                        event_type,
                        exchange=media_exchange,
                        routing_key=event_type
                )

                queue(conn.channel()).declare()
                routing_key = event_type

            with conn.Producer(exchange=media_exchange, serializer="json",
                               routing_key=routing_key) as producer:
                    producer.publish(params)

    # Example callback:
    # def callback(ch, method, properties, body)
    #   print " [x] Received %r" % (body,)
    def listen_event(self, queue_name, callback):
        with BrokerConnection(self.url) as conn:
            conn.ensure_connection()

            media_exchange = Exchange(
                    "simplenet",
                    type="direct",
                    durable=True
            )

            queue = Queue(
                    queue_name,
                    exchange=media_exchange,
                    routing_key=queue_name
            )

            with conn.Consumer([queue], callbacks=[callback]) as consumer:
                while True:
                    conn.drain_events()

    def bind_queue(self, queue_name, routing_key):
        with BrokerConnection(self.url) as conn:
            conn.ensure_connection()
            media_exchange = Exchange(
                    "simplenet",
                    type="direct",
                    durable=True
            )

            queue = Queue(
                    queue_name,
                    exchange=media_exchange,
                    routing_key=routing_key
            )

            queue(conn.channel()).declare()
