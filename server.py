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

from simplenet.common.config import config, set_logger

app = bottle.app()
LOG = logging.getLogger('simplenet.server')


@get('/neighborhoods')
def neighborhood_list():
    """
    ::

      GET /neighborhoods

    Get neighborhoods for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.neighborhood_list())


@post('/neighborhoods')
def neighborhood_create():
    """
    ::

      POST /neighborhood

    Create a new neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    neighborhood = manager.neighborhood_create(data)
    location = "neighborhoods/%s" % (neighborhood['id'])
    response.set_header("Location", location)
    return json.dumps(neighborhood)


@post('/neighborhoods/:neighborhood_id/devices')
def neighborhood_device_create(neighborhood_id):
    """
    ::

      POST /neighborhood/:neighborhood_id/devices

    Create a new device in neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_create(neighborhood_id, data)
    location = "devices/%s" % (device['id'])
    response.set_header("Location", location)
    return json.dumps(device)


@post('/neighborhoods/:neighborhood_id/vlans')
def neighborhood_vlan_create(neighborhood_id):
    """
    ::

      POST /neighborhood/:neighborhood_id/vlans

    Create a new vlan in neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    vlan = manager.vlan_create(neighborhood_id, data)
    location = "vlans/%s" % (vlan['id'])
    response.set_header("Location", location)
    return json.dumps(vlan)


@get('/neighborhoods/:neighborhood_id')
def neighborhood_info(neighborhood_id):
    """
    ::

      GET /neighborhoods/:neighborhood_id

    Get neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.neighborhood_info(neighborhood_id))


@get('/neighborhoods/by-name/:neighborhood_name')
def neighborhood_info_by_name(neighborhood_name):
    """
    ::

      GET /neighborhoods/by-name/:neighborhood_name

    Get neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.neighborhood_info_by_name(neighborhood_name))


@put('/neighborhoods/:neighborhood_id')
def neighborhood_update(neighborhood_id):
    """
    ::

      PUT /neighborhoods/:neighborhood_id

    Update neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    return json.dumps(manager.neighborhood_update(neighborhood_data))


@delete('/neighborhoods/:neighborhood_id')
def neighborhood_delete(neighborhood_id):
    """
    ::

      DELETE /neighborhoods/:neighborhood_id

    Deletes neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.neighborhood_delete(neighborhood_id))


@get('/devices')
def device_list():
    """
    ::

      GET /devices

    Get devices for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.device_list())


@get('/devices/:device_id')
def device_info(device_id):
    """
    ::

      GET /devices/:device_id

    Get device informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.device_info(device_id))


@post('/devices/:device_id/vlans')
def device_add_vlan(device_id):
    """
    ::

      POST /devices/:device_id/vlans

    Attach vlan to device
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_add_vlan(device_id, data)
    location = "devices/relationship/%s" % (device['id'])
    response.set_header("Location", location)
    return json.dumps(device)


@delete('/devices/:device_id/vlans/:vlan_id')
def device_remove_vlan(device_id, vlan_id):
    """
    ::

      POST /devices/:device_id/vlans

    Attach vlan to device
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    device = manager.device_remove_vlan(device_id, vlan_id)
    return json.dumps(device)


@get('/devices/by-name/:device_name')
def device_info_by_name(device_name):
    """
    ::

      GET /devices/by-name/:device_name

    Get device informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.device_info_by_name(device_name))


@put('/devices/:device_id')
def device_update(device_id):
    """
    ::

      PUT /devices/:device_id

    Update device informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    return json.dumps(manager.device_update(device_data))


@delete('/devices/:device_id')
def device_delete(device_id):
    """
    ::

      DELETE /devices/:device_id

    Deletes device
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.device_delete(device_id))


@post('/vlans/:vlan_id/subnets')
def vlan_subnet_create(vlan_id):
    """
    ::

      POST /vlan/:vlan_id/subnets

    Create a new subnet in vlan
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    subnet = manager.subnet_create(vlan_id, data)
    location = "subnets/%s" % (subnet['id'])
    response.set_header("Location", location)
    return json.dumps(subnet)


@get('/vlans/:vlan_id')
def vlan_info(vlan_id):
    """
    ::

      GET /vlans/:vlan_id

    Get vlan informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.vlan_info(vlan_id))


@get('/vlans/by-name/:vlan_name')
def vlan_info_by_name(vlan_name):
    """
    ::

      GET /vlans/by-name/:vlan_name

    Get vlan informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.vlan_info_by_name(vlan_name))

@get('/vlans')
def vlan_list():
    """
    ::

      GET /vlans

    Get vlans for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.vlan_list())


@delete('/vlans/:vlan_id')
def vlan_delete(vlan_id):
    """
    ::

      DELETE /vlans/:vlan_id

    Deletes vlan
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.vlan_delete(vlan_id))


@post('/subnets/:subnet_id/ips')
def subnet_ip_create(subnet_id):
    """
    ::

      POST /subnet/:subnet_id/ips

    Create a new ip in subnet
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    ip = manager.ip_create(subnet_id, data)
    location = "ips/%s" % (ip['id'])
    response.set_header("Location", location)
    return json.dumps(ip)


@get('/subnets/:subnet_id')
def subnet_info(subnet_id):
    """
    ::

      GET /subnets/:subnet_id

    Get subnet informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.subnet_info(subnet_id))


@get('/subnets/by-cidr/:subnet_ip/:subnet_mask')
def subnet_info_by_cidr(subnet_ip, subnet_mask):
    """
    ::

      GET /subnets/by-cidr/:subnet_ip/:subnet_mask

    Get subnet informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.subnet_info_by_cidr('%s/%s' % (subnet_ip, subnet_mask)))


@get('/subnets')
def subnet_list():
    """
    ::

      GET /subnets

    Get subnets for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.subnet_list())


@delete('/subnets/:subnet_id')
def subnet_delete(subnet_id):
    """
    ::

      DELETE /subnets/:subnet_id

    Deletes subnet
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.subnet_delete(subnet_id))


@get('/ips/:ip_id')
def ip_info(ip_id):
    """
    ::

      GET /ips/:ip_id

    Get ip informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.ip_info(ip_id))


@get('/ips/by-ip/:ip')
def ip_info_by_ip(ip):
    """
    ::

      GET /ips/by-ip/:ip

    Get ip informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.ip_info_by_ip(ip))


@get('/ips')
def ip_list():
    """
    ::

      GET /ips

    Get ips for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.ip_list())


@delete('/ips/:ip_id')
def ip_delete(ip_id):
    """
    ::

      DELETE /ips/:ip_id

    Deletes ip
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return json.dumps(manager.ip_delete(ip_id))


def create_manager(network_appliance):
#    network_appliance_token = request.headers.get("x-simplenet-network_appliance-token")
#    if not network_appliance_token:
#        abort(401, 'No x-simplenet-network_appliance-token header provided')

#    username, password = parse_token(network_appliance_token)

    module = __import__("simplenet.network_appliances.%s" % network_appliance)
    module = getattr(module.network_appliances, network_appliance)

    return module.Net()


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


