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
import logging

from bottle import delete, put, get, post
from bottle import request, response
from simplenet.common.http_auth import cas_authenticate, authorize

from simplenet.common.config import config, set_logger, get_rolesdb
from simplenet.common.http_utils import (
    reply_json, create_manager, validate_input
)

LOG = logging.getLogger('simplenet.server')

cas_endpoint = config.get("authentication", "cas_endpoint")
cas_sys_endpoint = config.get("authentication", "cas_sys_endpoint")
cas_service  = config.get("authentication", "cas_service")
user_roles = get_rolesdb()

## Generic Resource List
@get('/<resource>/list')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "ro")
@reply_json
def generic_resources_list(resource):
    """
    ::

      GET /<resource>/list

    Retrieves all entries from resource
    """
    manager = create_manager('base')
    try:
        _list = getattr(manager, '%s_list' % resource[:-1])
        return _list()
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Info
@get('/<resource>/<resource_id>/info')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "ro")
@reply_json
def generic_resource_info(resource, resource_id):
    """
    ::

      GET /<resource>/<resource_id>/info

    Retrieves resource information
    """
    manager = create_manager('base')
    try:
        _info = getattr(manager, '%s_info' % resource[:-1])
        return _info(resource_id)
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Info by name, cidr, ip
@get('/<resource>/by-<resource_type>/<resource_value>')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "ro")
@reply_json
def generic_resource_info_by_field(resource, resource_type, resource_value):
    """
    ::

      GET /<resource>/by-<resource_type>/<resource_value>

    Retrieves resource information by type
    """
    manager = create_manager('base')
    try:
        _info = getattr(manager, '%s_info_by_%s' % (resource[:-1], resource_type))
        return _info(resource_value)
    except AttributeError:
        raise FeatureNotAvailable()


# Generic list by parent
@get('/<resource>/list-by-<relationship_type>/<relationship_value>')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "ro")
@reply_json
def generic_resource_list_by_relationship(resource, relationship_type, relationship_value):
    """
    ::

      GET /<resource>/list-by-<relationship_type>/<relationship_value>

    List devices
    """
    manager = create_manager('base')
    try:
        _list = getattr(manager, '%s_list_by_%s' % (resource[:-1], relationship_type))
        return _list(relationship_value)
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Deletion
@delete('/<resource>/<resource_id>/delete')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@reply_json
def generic_resource_delete(resource, resource_id):
    """
    ::

      DELETE /<resource>/<resource_id>/delete

    Deletes resource
    """
    manager = create_manager('base')
    try:
        _delete = getattr(manager, '%s_delete' % (resource[:-1]))
        return _delete(resource_id)
    except AttributeError:
        raise FeatureNotAvailable()


@post('/datacenters')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(name=str)
@reply_json
def datacenter_create():
    """
    ::

      POST /datacenters

    Create a new datacenter
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    datacenter = manager.datacenter_create(data)
    location = "datacenters/%s" % (datacenter['id'])
    response.set_header("Location", location)
    return datacenter


@post('/datacenters/<datacenter_id>/zones')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(name=str)
@reply_json
def datacenter_zone_create(datacenter_id):
    """
    ::

      POST /datacenter/<datacenter_id>/zones

    Create a new zone in datacenter
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    zone = manager.zone_create(datacenter_id, data)
    location = "zones/%s" % (zone['id'])
    response.set_header("Location", location)
    return zone


@post('/zones/<zone_id>/devices')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(name=str)
@reply_json
def zone_device_create(zone_id):
    """
    ::

      POST /zone/<zone_id>/devices

    Create a new device in zone
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_create(zone_id, data)
    location = "devices/%s" % (device['id'])
    response.set_header("Location", location)
    return device


@post('/zones/<zone_id>/vlans')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(name=str)
@reply_json
def zone_vlan_create(zone_id):
    """
    ::

      POST /zone/<zone_id>/vlans

    Create a new vlan in zone
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    vlan = manager.vlan_create(zone_id, data)
    location = "vlans/%s" % (vlan['id'])
    response.set_header("Location", location)
    return vlan


@post('/devices/<device_id>/vlans')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(vlan_id=str)
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

@post('/devices/<device_id>/anycasts')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(anycast_id=str)
@reply_json
def device_add_anycast(device_id):
    """
    ::

      POST /devices/<device_id>/anycasts

    Attach vlan to device
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    device = manager.device_add_anycast(device_id, data)
    location = "devices/relationship/%s" % (device['id'])
    response.set_header("Location", location)
    return device


@delete('/devices/<device_id>/vlans/<vlan_id>')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
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


@post('/anycasts')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(cidr=str)
@reply_json
def anycast_create():
    """
    ::

      POST /anycasts

    Create a new anycast range
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    anycast = manager.anycast_create(data)
    location = "anycasts/%s" % (anycast['id'])
    response.set_header("Location", location)
    return anycast


@post('/vlans/<vlan_id>/subnets')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(cidr=str)
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


@post('/anycasts/<anycast_id>/ipsanycast')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(ip=str)
@reply_json
def anycast_ipanycast_create(anycast_id):
    """
    ::

      POST /anycasts/<anycast_id>/ipsanycast

    Create a new ip in anycast subnet
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    ip = manager.ipanycast_create(anycast_id, data)
    location = "ipsanycast/%s" % (ip['id'])
    response.set_header("Location", location)
    return ip


@post('/subnets/<subnet_id>/ips')
@cas_authenticate(servers=[cas_endpoint, cas_sys_endpoint], service=cas_service)
@authorize(user_roles, "rw")
@validate_input(ip=str)
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
