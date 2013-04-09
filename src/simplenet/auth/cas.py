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

from simplenet.common.http_utils import cache
from simplenet.common.config import config

from locautils.cas import CASClient, CasError

cas_endpoint = config.get("authentication", "cas_endpoint")
cas_sys_endpoint = config.get("authentication", "cas_sys_endpoint")
cas_service  = config.get("authentication", "cas_service")
user_roles = get_rolesdb()

class Auth(object)
    @cache
    def authenticate(self, request):
        cas_ticket = request.query.get("ticket")
        if not cas_ticket:
            abort(403, "Null Authentication Ticket (CAS)")

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
        request["authentication_info"] = user_info
        if self.authorize(user_info):

        return f(*args, **kwargs)

    def authorize(self, rolecfg=None, required_role=None):
        # TODO: Use CAS Authority for ACLs
        username = request["authentication_info"]["cn"][0].lower().replace(" ",".")
        if username not in rolecfg[required_role]:
            abort(403, "Forbidden")

class Load(Auth):
    pass
