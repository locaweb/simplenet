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
# @author: Eduardo Scarpelini (odraude), Locaweb.
# @author: Juliano Martinez (ncode), Locaweb.

import os

from functools import wraps
from bottle import response

try:
    from simplejson import dumps
except ImportError:
    from json import dumps


def reply_json(f):
    @wraps(f)
    def json_dumps(*args, **kwargs):
        r = f(*args, **kwargs)
        response.content_type = "application/json; charset=UTF-8"
        if r and type(r) in (dict, list, tuple):
            return dumps(r)
        if r and type(r) is str:
            return r
    return json_dumps

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
