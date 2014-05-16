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

from bottle import delete, put, get, post
from bottle import abort, request, response

from simplenet.common.auth import handle_auth
from simplenet.common.config import config, get_logger
from simplenet.exceptions import (
    FeatureNotAvailable, EntityNotFound,
    OperationNotPermited, FeatureNotAvailable
)
from simplenet.common.http_utils import (
    reply_json, create_manager
)

logger = get_logger()

@get('/v1/<network_appliance>/policies/<owner_type>/<id>')
@handle_auth
@reply_json
def policy_info(network_appliance, owner_type, id):
    """
    ::

      GET /v1/<network_appliance>/policies/<owner_type>/<id>

    Get policy informations
    """
    manager = create_manager(network_appliance)
    return manager.policy_info(owner_type, id)


@post('/v1/<network_appliance>/policies/<owner_type>/<id>')
@handle_auth
@reply_json
def policy_create(network_appliance, owner_type, id):
    """
    ::

      POST /v1/<network_appliance>/policies/<owner_type>/<id>

    Create a new policy
    """
    manager = create_manager(network_appliance)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    policy = manager.policy_create(owner_type, id, data)
    location = "%s/policies/%s/%s" % (network_appliance, owner_type, policy['id'])
    response.set_header("Location", location)
    return policy


@delete('/v1/<network_appliance>/policies/<owner_type>/<id>')
@handle_auth
@reply_json
def policy_delete(network_appliance, owner_type, id):
    """
    ::

      DELETE /v1/<network_appliance>/policies/<owner_type>/<owner_id>

    Deletes policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_delete(owner_type, id)


@get('/v1/<network_appliance>/policies/by-type/<owner_type>')
@handle_auth
@reply_json
def policy_list(network_appliance, owner_type):
    """
    ::

      GET /v1/<network_appliance>/policies/<owner_type>

    Get all policy
    """
    manager = create_manager(network_appliance)
    return manager.policy_list(owner_type)


@get('/v1/<network_appliance>/policies/by-owner/<owner_type>/<owner_id>')
@handle_auth
@reply_json
def policy_list_by_owner(network_appliance, owner_type, owner_id):
    """
    ::

      GET /v1/<network_appliance>/policies/by-owner/<owner_type>/<owner_id>

    Get all policy from a given owner
    """
    manager = create_manager(network_appliance)
    return manager.policy_list_by_owner(owner_type, owner_id)
