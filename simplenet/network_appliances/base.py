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

from simplenet.exceptions import FeatureNotImplemented
from simplenet.views.format_view import FormatView


class SimpleNet(object):

    def __init__(self):
        self.connection = False
        self.format_for = FormatView()

    def neighborhood_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def neighborhood_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def vlan_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def subnet_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def ip_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_list(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_create(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_info(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_update(self, *args, **kawrgs):
        raise FeatureNotImplemented()

    def policy_delete(self, *args, **kawrgs):
        raise FeatureNotImplemented()
