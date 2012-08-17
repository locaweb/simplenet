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
# @author: Thiago Morello (morellon), Locaweb.
# @author: Willian Molinari (PotHix), Locaweb.
# @author: Juliano Martinez (ncode), Locaweb.

class FormatView(object):

    def neighborhood(self, id, name):
        return {
            'id': id,
            'name': name,
        }

    def vlan(self, id, name, neighborhood_id):
        return {
            'id': id,
            'name': name,
            'neighborhood_id': neighborhood_id
        }

    def subnet(self, id, cidr, vlan_id):
        return {
            'id': id,
            'cidr': cidr,
            'vlan_id': vlan_id
        }

    def ip(self, id, ip, subnet_id):
        return {
            'id': id,
            'ip': ip,
            'subnet_id': subnet_id
        }

    def device(self, id, name, neighborhood_id):
        return {
            'id': id,
            'name': name,
            'neighborhood_id': neighborhood_id
        }

    def policy(self, policy):
        return policy.to_dict()
