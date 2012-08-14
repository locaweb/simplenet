#!/usr/bin/python

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

from gevent import monkey
monkey.patch_all()

import os
import grp
import pwd
import json
import time
import base64
import logging

import bottle
from bottle import delete, put, get, post, error, redirect, run, debug
from bottle import abort, request, ServerAdapter, response, static_file
from bottle import error, HTTPError

from common.config import config, set_logger

app = bottle.app()
LOG = logging.getLogger('simplenet.server')


@get('/:network_appliance/neighborhoods')
def neighborhood_list(network_appliance):
    """
    ::

      GET /:network_appliance/neighborhoods

    Get neighborhoods for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    return json.dumps(manager.neighborhood_list())


@post('/:network_appliance/neighborhoods')
def neighborhood_create(network_appliance):
    """
    ::

      POST /:network_appliance/neighborhood

    Create a new neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    neighborhood = manager.neighborhood_create(data)
    location = "/%s/neighborhoods/%s" % (network_appliance, neighborhood["id"])
    response.set_header("Location", location)
    return json.dumps(neighborhood)


@get('/:network_appliance/neighborhoods/:neighborhood_id')
def neighborhood_info(network_appliance, neighborhood_id):
    """
    ::

      GET /:network_appliance/neighborhoods/:neighborhood_id

    Get neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    return json.dumps(manager.neighborhood_info(neighborhood_id))


@put('/:network_appliance/neighborhoods/:neighborhood_id')
def neighborhood_update(network_appliance, neighborhood_id):
    """
    ::

      PUT /:network_appliance/:id

    Update neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    return json.dumps(manager.neighborhood_update(neighborhood_data))


@delete('/:network_appliance/neighborhoods/:neighborhood_id')
def neighborhood_delete(network_appliance, neighborhood_id):
    """
    ::

      DELETE /:network_appliance/neighborhoods/:neighborhood_id

    Deletes neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    return json.dumps(manager.neighborhood_delete(neighborhood_id))


def create_manager(network_appliance):
#    network_appliance_token = request.headers.get("x-simplenet-network_appliance-token")
#    if not network_appliance_token:
#        abort(401, 'No x-simplenet-network_appliance-token header provided')

#    username, password = parse_token(network_appliance_token)

    module = __import__("simplenet.network_appliances.%s" % network_appliance)
    module = getattr(module.network_appliances, network_appliance)

    return module.Stack({
        "api_server": host,
        "username": username,
        "password": password
    })


def main():
#    os.setgid(grp.getgrnam('nogroup')[2])
#    os.setuid(pwd.getpwnam(config.get("server", "user"))[2])
    debug(config.getboolean("server", "debug"))
    port = config.getint("server", "port")
    bind_addr = config.get("server", "bind_addr")
    set_logger()
    LOG.info("Starting Simplestack server")
    run(host=bind_addr, port=port, server="gevent")

if __name__ == '__main__':
    main()


