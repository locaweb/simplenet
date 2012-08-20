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
from simplenet.common.http_utils import reply_json

app = bottle.app()
LOG = logging.getLogger('simplenet.server')


@get('/neighborhoods')
@reply_json
def neighborhood_list():
    """
    ::

      GET /neighborhoods

    Get neighborhoods for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.neighborhood_list()


@post('/neighborhoods')
@reply_json
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
    return neighborhood


@post('/neighborhoods/:neighborhood_id/devices')
@reply_json
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
    return device


@post('/neighborhoods/:neighborhood_id/vlans')
@reply_json
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
@reply_json
def neighborhood_info(neighborhood_id):
    """
    ::

      GET /neighborhoods/:neighborhood_id

    Get neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.neighborhood_info(neighborhood_id)


@get('/neighborhoods/by-name/:neighborhood_name')
@reply_json
def neighborhood_info_by_name(neighborhood_name):
    """
    ::

      GET /neighborhoods/by-name/:neighborhood_name

    Get neighborhood informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.neighborhood_info_by_name(neighborhood_name)


@delete('/neighborhoods/:neighborhood_id')
@reply_json
def neighborhood_delete(neighborhood_id):
    """
    ::

      DELETE /neighborhoods/:neighborhood_id

    Deletes neighborhood
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    manager.neighborhood_delete(neighborhood_id)


@get('/devices')
@reply_json
def device_list():
    """
    ::

      GET /devices

    Get devices for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.device_list()


@get('/devices/:device_id')
@reply_json
def device_info(device_id):
    """
    ::

      GET /devices/:device_id

    Get device informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.device_info(device_id)


@post('/devices/:device_id/vlans')
@reply_json
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
    return device


@delete('/devices/:device_id/vlans/:vlan_id')
@reply_json
def device_remove_vlan(device_id, vlan_id):
    """
    ::

      POST /devices/:device_id/vlans

    Attach vlan to device
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    device = manager.device_remove_vlan(device_id, vlan_id)
    return device


@get('/devices/by-name/:device_name')
@reply_json
def device_info_by_name(device_name):
    """
    ::

      GET /devices/by-name/:device_name

    Get device informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.device_info_by_name(device_name)


@delete('/devices/:device_id')
@reply_json
def device_delete(device_id):
    """
    ::

      DELETE /devices/:device_id

    Deletes device
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.device_delete(device_id)


@post('/vlans/:vlan_id/subnets')
@reply_json
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
    return subnet


@get('/vlans/:vlan_id')
@reply_json
def vlan_info(vlan_id):
    """
    ::

      GET /vlans/:vlan_id

    Get vlan informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.vlan_info(vlan_id)


@get('/vlans/by-name/:vlan_name')
@reply_json
def vlan_info_by_name(vlan_name):
    """
    ::

      GET /vlans/by-name/:vlan_name

    Get vlan informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.vlan_info_by_name(vlan_name)


@get('/vlans')
@reply_json
def vlan_list():
    """
    ::

      GET /vlans

    Get vlans for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.vlan_list()


@delete('/vlans/:vlan_id')
@reply_json
def vlan_delete(vlan_id):
    """
    ::

      DELETE /vlans/:vlan_id

    Deletes vlan
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.vlan_delete(vlan_id)


@post('/subnets/:subnet_id/ips')
@reply_json
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
    return ip


@get('/subnets/:subnet_id')
@reply_json
def subnet_info(subnet_id):
    """
    ::

      GET /subnets/:subnet_id

    Get subnet informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.subnet_info(subnet_id)


@get('/subnets/by-cidr/:subnet_ip/:subnet_mask')
@reply_json
def subnet_info_by_cidr(subnet_ip, subnet_mask):
    """
    ::

      GET /subnets/by-cidr/:subnet_ip/:subnet_mask

    Get subnet informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.subnet_info_by_cidr('%s/%s' % (subnet_ip, subnet_mask))


@get('/subnets')
@reply_json
def subnet_list():
    """
    ::

      GET /subnets

    Get subnets for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.subnet_list()


@delete('/subnets/:subnet_id')
@reply_json
def subnet_delete(subnet_id):
    """
    ::

      DELETE /subnets/:subnet_id

    Deletes subnet
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.subnet_delete(subnet_id)


@get('/ips/:ip_id')
@reply_json
def ip_info(ip_id):
    """
    ::

      GET /ips/:ip_id

    Get ip informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.ip_info(ip_id)


@get('/ips/by-ip/:ip')
@reply_json
def ip_info_by_ip(ip):
    """
    ::

      GET /ips/by-ip/:ip

    Get ip informations
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.ip_info_by_ip(ip)


@get('/ips')
@reply_json
def ip_list():
    """
    ::

      GET /ips

    Get ips for a given pool
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.ip_list()


@delete('/ips/:ip_id')
@reply_json
def ip_delete(ip_id):
    """
    ::

      DELETE /ips/:ip_id

    Deletes ip
    """
    response.content_type = "application/json"
    manager = create_manager('base')
    return manager.ip_delete(ip_id)


@get('/:network_appliance/policy/:owner_type/:policy_id')
@reply_json
def policy_info(network_appliance, owner_type, policy_id):
    """
    ::

      GET /:network_appliance/policy/:owner_type/:policy_id

    Get policy informations
    """
    print network_appliance, owner_type, policy_id
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    print network_appliance, owner_type, policy_id
    return manager.policy_info(owner_type, policy_id)

@post('/:network_appliance/policy/:owner_type/:owner_id')
@reply_json
def policy_create(network_appliance, owner_type, owner_id):
    """
    ::

      POST /:network_appliance/policy/:owner_type/:owner_id

    Create a new policy
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    print owner_id
    policy = manager.policy_create(owner_type, owner_id, data)
    location = "%s/policy/%s/%s" % (network_appliance, owner_type, policy['id'])
    response.set_header("Location", location)
    return policy


@delete('/:network_appliance/policy/:owner_type/:policy_id')
@reply_json
def policy_delete(network_appliance, owner_type, policy_id):
    """
    ::

      DELETE /:network_appliance/policy/:owner_type/:policy_id

    Deletes policy
    """
    response.content_type = "application/json"
    manager = create_manager(network_appliance)
    return manager.policy_delete(owner_type, policy_id)


#@get('/:network_appliance/policy/:owner_type')
#@reply_json
#def policy_list(network_appliance, owner_type):
#    """
#    ::
#
#      GET /:network_appliance/policy
#
#    Get all policy
#    """
#    response.content_type = "application/json"
#    manager = create_manager(network_appliance)
#    return manager.policy_list(owner_type)


#@get('/:network_appliance/policy/by-owner/:owner_type/:owner_id')
#@reply_json
#def policy_list_by_owner(network_appliance, owner_type, owner_id=None):
#    """
#    ::
#
#      GET /policys
#
#    Get policys for a given pool
#    """
#    response.content_type = "application/json"
#    manager = create_manager(network_appliance)
#    return manager.policy_list_by_owner(owner_type, owner_id)


#@error(400)
#@reply_json
#def error400(err):
#    return {"status": err.status, "message": err.output}
#
#
#@error(403)
#@reply_json
#def error403(err):
#    return {"status": err.status, "message": err.output}
#
#
#@error(404)
#@reply_json
#def error404(err):
#    return {"status": err.status, "message": err.output}
#
#
#@error(405)
#@reply_json
#def error405(err):
#    return {"status": err.status, "message": err.output}
#
#
#@error(500)
#@reply_json
#def error500(err):
#    return {"status": err.status, "message": err.exception.__repr__()}
#
#
#@error(501)
#@reply_json
#def error501(err):
#    return {"status": err.status, "message": err.output}


def create_manager(network_appliance):
#    network_appliance_token = request.headers.get("x-simplenet-network_appliance-token")
#    if not network_appliance_token:
#        abort(401, 'No x-simplenet-network_appliance-token header provided')

#    username, password = parse_token(network_appliance_token)

    _module_ = "simplenet.network_appliances.%s" % network_appliance
    if not os.path.isfile("%s.py" % _module_.replace('.', '/')):
        raise RuntimeError("The requested module is missing")
    module = __import__(_module_)
    module = getattr(module.network_appliances, network_appliance)

    return module.Net()


def main():
#    os.setgid(grp.getgrnam('nogroup')[2])
#    os.setuid(pwd.getpwnam(config.get("server", "user"))[2])
#    debug(config.getboolean("server", "debug"))
    port = config.getint("server", "port")
    bind_addr = config.get("server", "bind_addr")
    set_logger()
    LOG.info("Starting Simplestack server")
    run(host=bind_addr, port=port, server="gevent")
    #run(host=bind_addr, port=port)

if __name__ == '__main__':
    main()


