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

@post('/switchs')
@handle_auth
@reply_json
def switch_create():
    """
    ::

      POST /switchs

    Create a new switch device
    """
    manager = create_manager('switch')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    switch = manager.switch_create(data=data)
    location = "switchs/%s" % (switch['id'])
    response.set_header("Location", location)
    return switch

@post('/switchs/<switch_id>/interfaces')
@handle_auth
@reply_json
def switch_add_interface(switch_id):
    """
    ::

      POST /switchs/<switch_id>/interfaces

    Attach Interface to Switch
    """
    manager = create_manager('switch')
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    data = json.loads(data)
    interface = manager.switch_add_interface(switch_id, data)
    return interface

@delete('/switchs/<switch_id>/interfaces/<interface_id>')
@handle_auth
@reply_json
def switch_remove_interface(switch_id, interface_id):
    """
    ::

      DELETE /switchs/<switch_id>/interfaces/<interface_id>

    Detach Interface to Switch
    """
    manager = create_manager('switch')
    interface = manager.switch_remove_interface(switch_id, interface_id)
    return interface
