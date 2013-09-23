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

from bottle import abort, delete, get, post
from bottle import request, response

from simplenet.common.auth import handle_auth
from simplenet.common.config import get_logger
from simplenet.common.http_utils import (
    reply_json, create_manager, validate_input
)
from simplenet.exceptions import (
    FeatureNotAvailable
)

logger = get_logger()

def generic_router(resource):
    if resource == 'firewalls':
        return 'firewall'
    elif resource == 'switchs':
        return 'switch'
    elif resource == 'dhcps':
        return 'dhcp'
    else:
        return 'base'


@get('/prober')
@handle_auth
@reply_json
def generic_prober():
    """
    ::

      GET /prober

    Do a SQL query for DB status
    """
    manager = create_manager('base')
    try:
        _list = getattr(manager, 'prober')
        return _list()
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource List
@get('/<resource>/list')
@handle_auth
@reply_json
def generic_resources_list(resource):
    """
    ::

      GET /<resource>/list

    Retrieves all entries from resource
    """
    manager = create_manager(generic_router(resource))
    try:
        _list = getattr(manager, '%s_list' % resource[:-1])
        return _list()
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Info
@get('/<resource>/<resource_id>/info')
@handle_auth
@reply_json
def generic_resource_info(resource, resource_id):
    """
    ::

      GET /<resource>/<resource_id>/info

    Retrieves resource information
    """
    manager = create_manager(generic_router(resource))
    try:
        _info = getattr(manager, '%s_info' % resource[:-1])
        return _info(resource_id)
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Info by name, cidr, ip
@get('/<resource>/by-<resource_type>/<resource_value>')
@handle_auth
@reply_json
def generic_resource_info_by_field(resource, resource_type, resource_value):
    """
    ::

      GET /<resource>/by-<resource_type>/<resource_value>

    Retrieves resource information by type
    """
    manager = create_manager(generic_router(resource))
    try:
        _info = getattr(manager, '%s_info_by_%s' % (resource[:-1], resource_type))
        return _info(resource_value)
    except AttributeError:
        raise FeatureNotAvailable()


# Generic list by parent
@get('/<resource>/list-by-<relationship_type>/<relationship_value>')
@handle_auth
@reply_json
def generic_resource_list_by_relationship(resource, relationship_type, relationship_value):
    """
    ::

      GET /<resource>/list-by-<relationship_type>/<relationship_value>

    List devices
    """
    manager = create_manager(generic_router(resource))
    try:
        _list = getattr(manager, '%s_list_by_%s' % (resource[:-1], relationship_type))
        return _list(relationship_value)
    except AttributeError:
        raise FeatureNotAvailable()


## Generic Resource Deletion
@delete('/<resource>/<resource_id>/delete')
@handle_auth
@reply_json
def generic_resource_delete(resource, resource_id):
    """
    ::

      DELETE /<resource>/<resource_id>/delete

    Deletes resource
    """
    manager = create_manager(generic_router(resource))
    try:
        _delete = getattr(manager, '%s_delete' % (resource[:-1]))
        return _delete(resource_id)
    except AttributeError:
        raise FeatureNotAvailable()


@post('/datacenters')
@handle_auth
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
@handle_auth
@validate_input(name=str)
@reply_json
def datacenter_zone_create(datacenter_id):
    """
    ::

      POST /datacenters/<datacenter_id>/zones

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


@post('/dhcps')
@handle_auth
@validate_input(name=str)
@reply_json
def dhcp_create():
    """
    ::

      POST /dhcps

    Create a new DHCP device
    """
    manager = create_manager('dhcp')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    dhcp = manager.dhcp_create(data=data)
    location = "dhcps/%s" % (dhcp['id'])
    response.set_header("Location", location)
    return dhcp


@post('/dhcps/<dhcp_id>/vlans')
@handle_auth
@validate_input(vlan_id=str)
@reply_json
def dhcp_add_vlan(dhcp_id):
    """
    ::

      POST /dhcps/<dhcp_id>/vlans

    Attach vlan to DHCP device
    """
    manager = create_manager('dhcp')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    dhcp = manager.dhcp_add_vlan(dhcp_id, data['vlan_id'])
    location = "dhcps/relationship/%s" % (dhcp['id'])
    response.set_header("Location", location)
    return dhcp


@delete('/dhcps/<dhcp_id>/vlans/<vlan_id>')
@handle_auth
@reply_json
def dhcp_remove_vlan(dhcp_id, vlan_id):
    """
    ::

      POST /dhcps/<dhcp_id>/vlans/<vlan_id>

    Attach vlan to DHCP device
    """
    manager = create_manager('dhcp')
    dhcp = manager.dhcp_remove_vlan(dhcp_id, vlan_id)
    return dhcp


@post('/firewalls')
@handle_auth
@validate_input(name=str)
@reply_json
def firewall_create():
    """
    ::

      POST /firewalls

    Create a new firewall device
    """
    manager = create_manager('firewall')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    firewall = manager.firewall_create(data=data)
    location = "firewalls/%s" % (firewall['id'])
    response.set_header("Location", location)
    return firewall


@post('/zones/<zone_id>/vlans')
@handle_auth
@validate_input(name=str)
@reply_json
def zone_vlan_create(zone_id):
    """
    ::

      POST /zones/<zone_id>/vlans

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


@post('/firewalls/<firewall_id>/vlans')
@handle_auth
@validate_input(vlan_id=str)
@reply_json
def firewall_add_vlan(firewall_id):
    """
    ::

      POST /firewalls/<firewall_id>/vlans

    Attach vlan to firewall device
    """
    manager = create_manager('firewall')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    firewall = manager.firewall_add_vlan(firewall_id, data)
    location = "firewalls/relationship/%s" % (firewall['id'])
    response.set_header("Location", location)
    return firewall


@post('/firewalls/<firewall_id>/anycasts')
@handle_auth
@validate_input(anycast_id=str)
@reply_json
def firewall_add_anycast(firewall_id):
    """
    ::

      POST /firewalls/<firewall_id>/anycasts

    Attach vlan to firewall device
    """
    manager = create_manager('firewall')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    firewall = manager.firewall_add_anycast(firewall_id, data)
    location = "firewall/relationship/%s" % (firewall['id'])
    response.set_header("Location", location)
    return firewall


@delete('/firewalls/<firewall_id>/vlans/<vlan_id>')
@handle_auth
@reply_json
def firewall_remove_vlan(firewall_id, vlan_id):
    """
    ::

      POST /firewalls/<firewall_id>/vlans/<vlan_id>

    Attach vlan to firewall device
    """
    manager = create_manager('firewall')
    firewall = manager.firewall_remove_vlan(firewall_id, vlan_id)
    return firewall


@delete('/firewalls/<firewall_id>/anycasts/<anycast_id>')
@handle_auth
@reply_json
def firewall_remove_anycast(firewall_id, anycast_id):
    """
    ::

      POST /firewalls/<firewall_id>/anycasts/<anycast_id>

    Attach anycasts to firewall device
    """
    manager = create_manager('firewall')
    firewall = manager.firewall_remove_anycast(firewall_id, anycast_id)
    return firewall


@post('/anycasts')
@handle_auth
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
@handle_auth
@validate_input(cidr=str)
@reply_json
def vlan_subnet_create(vlan_id):
    """
    ::

      POST /vlans/<vlan_id>/subnets

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


@post('/anycasts/<anycast_id>/anycastips')
@handle_auth
@validate_input(ip=str)
@reply_json
def anycast_anycastip_create(anycast_id):
    """
    ::

      POST /anycasts/<anycast_id>/anycastips

    Create a new ip in anycast subnet
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    ip = manager.anycastip_create(anycast_id, data)
    location = "anycastips/%s" % (ip['id'])
    response.set_header("Location", location)
    return ip


@post('/subnets/<subnet_id>/ips')
@handle_auth
@validate_input(ip=str)
@reply_json
def subnet_ip_create(subnet_id):
    """
    ::

      POST /subnets/<subnet_id>/ips

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


@post('/interfaces')
@handle_auth
@reply_json
def interface_create():
    """
    ::

      POST /interfaces

    Create a new interface
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    interface = manager.interface_create(data)
    location = "interfaces/%s" % (interface['id'])
    response.set_header("Location", location)
    return interface


@post('/interfaces/<interface_id>/ips')
@handle_auth
@reply_json
def interface_add_ip(interface_id):
    """
    ::

      POST /interfaces/<interface_id>/ips

    Attach IP to interface
    """
    manager = create_manager('base')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    interface = manager.interface_add_ip(interface_id, data)
    return interface


@delete('/interfaces/<interface_id>/ips/<ip_id>')
@handle_auth
@reply_json
def interface_remove_ip(interface_id, ip_id):
    """
    ::

      DELETE /interfaces/<interface_id>/ips/<ip_id>

    Detach ip from interface
    """
    manager = create_manager('base')
    interface = manager.interface_remove_ip(interface_id, ip_id)
    return interface
