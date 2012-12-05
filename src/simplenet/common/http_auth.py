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
import logging
import hashlib

logger = logging.getLogger('simplenet.server')

__all__ = ["cas_authenticate", "authorize"]


def cas_authenticate(servers=None, service=None):
    def proxy(f):
        @wraps(f)
        def auth(*args, **kwargs):
            cas_ticket = request.query.get("ticket")
            if not cas_ticket:
                abort(403, "Null Authentication Ticket (CAS)")
            redis_db = RedisClient()
            auth_cache = redis_db.get_connection()
            m = hashlib.md5()
            m.update(cas_ticket)
            cas_hash = m.hexdigest()
            if (auth_cache.exists(cas_hash) == False):
                print "Not found " + cas_hash
                try:
                    logger.info("Trying to validate CAS ticket '%s' on server '%s'" % (cas_ticket, servers[0]))
                    user_info = CASClient(server=servers[0]).validate_ticket(ticket=cas_ticket, service=service)
                except CasError:
                    logger.exception("CAS ticket validation failed")
                    try:
                        logger.info("Trying to validate CAS-ticket '%s' on server '%s'" % (cas_ticket, servers[1]))
                        user_info = CASClient(server=servers[1]).validate_ticket(ticket=cas_ticket, service=service)
                    except CasError:
                        logger.exception("CAS ticket validation failed")
                        abort(403, "Invalid Authentication Ticket (CAS)")
                auth_cache.hset(cas_hash, "user_info", user_info)
                auth_cache.expire(cas_hash, 60)
                request["authentication_info"] = user_info
                return f(*args, **kwargs)
            else:
                print "FOund " + cas_hash
                request["authentication_info"] = literal_eval(auth_cache.hget(cas_hash, "user_info"))
                return f(*args, **kwargs)
        return auth
    return proxy


def authorize(rolecfg=None, required_role=None):
    def proxy(f):
        def auth(*args, **kwargs):
            # TODO: Use CAS Authority for ACLs
            username = request["authentication_info"]["cn"][0].lower().replace(" ",".")
            if username not in rolecfg[required_role]:
                abort(403, "Forbidden")
            return f(*args, **kwargs)
        return auth
    return proxy
