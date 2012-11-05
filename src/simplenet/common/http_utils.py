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

import os
import logging

from functools import wraps
from bottle import response, request, abort

from simplenet.common.config import config

try:
    from simplejson import dumps, loads
except ImportError:
    from json import dumps, loads

LOG = logging.getLogger('simplenet.server')


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
    auth_type = config.get('server', 'auth_type')
    if not 'disabled' in auth_type:
        _auth_ = 'simplenet.auth_methods.%s' % auth_type
        auth = __import__(_auth_)
        auth = getattr(_auth_, auth_type)
        auth.Policy(request)

    _module_ = "simplenet.network_appliances.%s" % network_appliance
    module = __import__(_module_)
    module = getattr(module.network_appliances, network_appliance)

    return module.Net()


def validate_input(src="query", *vargs, **vkwargs):
    """
    Usage:
    >>> @get('/test')
    ... @validate_input(name=str, age=int, email=re.compile("\w+@\w+.com"), gender=("M", "F"))
    ... def test():
    ...    data = json.loads(request.body.readline())
    ...    return data.get("name")
    """
    def proxy(f):
        @wraps(f)
        def validate(*args, **kwargs):
            psource = loads(request.body.readline())

            for param, ptype in vkwargs.iteritems():
                pvalue = psource.get(param, None)

                try:
                    # lambda
                    if isinstance(ptype, type(lambda: None)) and ptype.__name__ == '<lambda>':
                        if not ptype(pvalue):
                            raise InvalidParameter("False")
                        continue

                    if pvalue is None:
                        raise NullParameter("Error: the '%s' query param is null" % param)

                    # exact match
                    if type(ptype) in (str, unicode):
                        assert pvalue == ptype
                        continue
                    # valid option list
                    if type(ptype) in (list, tuple):
                        assert pvalue in ptype
                        continue
                    # int(), str(), etc
                    if type(ptype) is type:
                        ptype(pvalue)
                        continue
                    # regexp
                    if isinstance(ptype, _pattern_type):
                        assert ptype.search(pvalue) is not None
                        continue
                except NullParameter, e:
                    LOG.warn(str(e))
                    abort(400, str(e))
                except Exception, e:
                    LOG.warn("Error: the '%s' param has an unexpected type or an invalid format" % param) \
                    if logger else None
                    abort(400, "Error: '%s' query parameter has an unexpected type or an invalid format" % param)
            return f(*args, **kwargs)
        return validate
    return proxy

class InvalidParameter(Exception):
    pass

class NullParameter(Exception):
    pass
