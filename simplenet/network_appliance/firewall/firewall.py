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

import logging

from simplenet.exceptions import FeatureNotImplemented
from simplenet.views.format_view import FormatView

from simplenet.network_appliance.base import SimpleNet

LOG = logging.getLogger(__name__)


class Net(SimpleNet):

    def neighborhood_list(*args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_create(*args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_info(*args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_update(*args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_delete(*args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_list(*args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_create(*args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_info(*args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_update(*args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_delete(*args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_list(*args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_create(*args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_info(*args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_update(*args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_delete(*args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_list(*args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_create(*args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_info(*args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_update(*args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_delete(*args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_list(*args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_create(*args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_info(*args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_update(*args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_delete(*args, **kawrgs):
        raise FeatureNotImplemented()
