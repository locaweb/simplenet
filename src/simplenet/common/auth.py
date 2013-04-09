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
# @author: Luiz Ozaki, Locaweb.

__copyright__ = "Copyright 2012, Locaweb IDC"

from ast import literal_eval
from functools import wraps
from bottle import request, abort
from locautils.cas import CASClient, CasError
from simplenet.common.cache import RedisClient
import hashlib

logger = get_logger()

cas_endpoint = config.get("authentication", "cas_endpoint")
cas_sys_endpoint = config.get("authentication", "cas_sys_endpoint")
cas_service  = config.get("authentication", "cas_service")
user_roles = get_rolesdb()

def load_plugin(network_appliance):
    _module_ = "simplenet.network_appliances.%s" % network_appliance
    module = __import__(_module_)
    module = getattr(module.network_appliances, network_appliance)
    return module.Load()

def handle_auth():
    def proxy(f):
        @wraps(f)
        def auth(f):
            if not config.getboolean("authentication", "enabled"):
                return f(*args, **kwargs)
            authentication_plugin = config.get("authentication", "authentication_plugin")
            def authenticate(*args, **kwargs):
                auth = load_plugin(authentication_plugin)
                if auth.do(request):
                    return f(*args, **kwargs)
                else:
                    logger
                    abort(403, "Access denied")
        return auth
    return proxy
