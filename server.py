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

## Generic Resource List
@get('/<resource>/list')
@reply_json
def generic_resources_list(resource):
    """
    ::

      GET /<resource>/list

    Retrieves all entries from resource
    """
    manager = create_manager('base')
    _list = getattr(manager, '%s_list' % resource[:-1])
    return _list()


## Generic Resource Info
@get('/<resource>/<resource_id>/info')
@reply_json
def generic_resource_info(resource, resource_id):
    """
    ::

      GET /<resource>/<resource_id>/info

    Retrieves resource information
    """
    manager = create_manager('base')
    _info = getattr(manager, '%s_info' % resource[:-1])
    return _info(resource_id)


## Generic Resource Info by name, cidr, ip
@get('/<resource>/by-<resource_type>/<resource_value>')
@reply_json
def generic_resource_info_info_by_field(resource, resource_type, resource_value):
    """
    ::

      GET /<resource>/by-<resource_type>/<resource_value>

    Retrieves resource information by type
    """
    manager = create_manager('base')
    _info = getattr(manager, '%s_info_by_%s' % (resource[:-1], resource_type))
    manager = create_manager('base')
    return _info(resource_value)


## Generic Resource Deletion
@delete('/<resource>/<resource_id>/delete')
@reply_json
def generic_resource_delete(resource, resource_id):
    """
    ::

      DELETE /<resource>/<resource_id>/delete

    Deletes resource
    """
    manager = create_manager('base')
    _delete = getattr(manager, '%s_delete' % (resource[:-1]))
    manager = create_manager('base')
    return _delete(resource_id)


@post('/neighborhoods')
@reply_json
def neighborhood_create():
    """
    ::

      POST /neighborhood

    Create a new neighborhood
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    neighborhood = manager.neighborhood_create(data)
    location = "neighborhoods/%s" % (neighborhood['id'])
    response.set_header("Location", location)
    return neighborhood


@post('/neighborhoods/<neighborhood_id>/devices')
@reply_json
def neighborhood_device_create(neighborhood_id):
    """
    ::

      POST /neighborhood/<neighborhood_id>/devices

    Create a new device in neighborhood
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_create(neighborhood_id, data)
    location = "devices/%s" % (device['id'])
    response.set_header("Location", location)
    return device


@post('/neighborhoods/<neighborhood_id>/vlans')
@reply_json
def neighborhood_vlan_create(neighborhood_id):
    """
    ::

      POST /neighborhood/<neighborhood_id>/vlans

    Create a new vlan in neighborhood
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    vlan = manager.vlan_create(neighborhood_id, data)
    location = "vlans/%s" % (vlan['id'])
    response.set_header("Location", location)
    return json.dumps(vlan)


@post('/devices/<device_id>/vlans')
@reply_json
def device_add_vlan(device_id):
    """
    ::

      POST /devices/<device_id>/vlans

    Attach vlan to device
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_add_vlan(device_id, data)
    location = "devices/relationship/%s" % (device['id'])
    response.set_header("Location", location)
    return device


@delete('/devices/<device_id>/vlans/<vlan_id>')
@reply_json
def device_remove_vlan(device_id, vlan_id):
    """
    ::

      POST /devices/<device_id>/vlans/<vlan_id>

    Attach vlan to device
    """
    manager = create_manager('base')
    device = manager.device_remove_vlan(device_id, vlan_id)
    return device


@post('/vlans/<vlan_id>/subnets')
@reply_json
def vlan_subnet_create(vlan_id):
    """
    ::

      POST /vlan/<vlan_id>/subnets

    Create a new subnet in vlan
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    subnet = manager.subnet_create(vlan_id, data)
    location = "subnets/%s" % (subnet['id'])
    response.set_header("Location", location)
    return subnet


@post('/subnets/<subnet_id>/ips')
@reply_json
def subnet_ip_create(subnet_id):
    """
    ::

      POST /subnet/<subnet_id>/ips

    Create a new ip in subnet
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    ip = manager.ip_create(subnet_id, data)
    location = "ips/%s" % (ip['id'])
    response.set_header("Location", location)
    return ip


@get('/<network_appliance>/policy/<owner_type>/<policy_id>/info')
@reply_json
def policy_info(network_appliance, owner_type, policy_id):
    """
    ::

      GET /<network_appliance>/policy/<owner_type>/<policy_id>/info

    Get policy informations
    """
    manager = create_manager(network_appliance)
    return manager.policy_info(owner_type, policy_id)


@post('/<network_appliance>/policy/<owner_type>/<owner_id>')
@reply_json
def policy_create(network_appliance, owner_type, owner_id):
    """
    ::

      POST /<network_appliance>/policy/<owner_type>/<owner_id>

    Create a new policy
    """
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    policy = manager.policy_create(owner_type, owner_id, data)
    location = "%s/policy/%s/%s" % (network_appliance, owner_type, policy['id'])
    response.set_header("Location", location)
    return policy


@delete('/<network_appliance>/policy/<owner_type>/<policy_id>/delete')
@reply_json
def policy_delete(network_appliance, owner_type, policy_id):
    """
    ::

      DELETE /<network_appliance>/policy/<owner_type>/<policy_id>/delete

    Deletes policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_delete(owner_type, policy_id)


@get('/<network_appliance>/policy/<owner_type>/list')
@reply_json
def policy_list(network_appliance, owner_type):
    """
    ::

      GET /<network_appliance>/policy/<owner_type>/list

    Get all policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_list(owner_type)


@get('/:network_appliance/policy/by-owner/:owner_type/:owner_id/list')
@reply_json
def policy_list_by_owner(network_appliance, owner_type):
    """
    ::

      GET /policys

    Get policys for a given pool
    """
    manager = create_manager(network_appliance)
    return manager.policy_list_by_owner(owner_type, owner_id)


@error(400)
@reply_json
def error400(err):
    return {"status": err.status, "message": err.output}


@error(403)
@reply_json
def error403(err):
    return {"status": err.status, "message": err.output}


@error(404)
@reply_json
def error404(err):
    return {"status": err.status, "message": err.output}


@error(405)
@reply_json
def error405(err):
    return {"status": err.status, "message": err.output}


@error(500)
@reply_json
def error500(err):
    return {"status": err.status, "message": err.exception.__repr__()}


@error(501)
@reply_json
def error501(err):
    return {"status": err.status, "message": err.output}


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


