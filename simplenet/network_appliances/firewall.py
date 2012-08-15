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

from simplenet.db import models, db_utils
from simplenet.exceptions import EntityNotFound
from simplenet.network_appliances.base import SimpleNet

LOG = logging.getLogger(__name__)
session = db_utils.get_database_session()


class Net(SimpleNet):

    def neighborhood_list(self):
        ss = session.query(models.Neighborhood).all()
        neighborhoods = []
        for neighborhood in ss:
            neighborhoods.append(
                self.format_for.neighborhood(
                    neighborhood.id,
                    neighborhood.name
                )
            )
        return neighborhoods

    def neighborhood_create(self, data):
        if not 'name' in data:
            raise Exception('Missing value name')
        session.begin(subtransactions=True)
        try:
            session.add(models.Neighborhood(name=data['name']))
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return self._neighborhood_info_by_name(data['name'])

    def neighborhood_info(self, id):
        ss = session.query(models.Neighborhood).get(id)
        if not ss:
            raise EntityNotFound('Neighborhood', id)
        return self.format_for.neighborhood(ss.id, ss.name)

    def _neighborhood_info_by_name(self, name):
        ss = session.query(models.Neighborhood).filter_by(name=name).first()
        return self.format_for.neighborhood(
            id = ss.id,
            name = ss.name
        )

    def neighborhood_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def neighborhood_delete(self, id):
        ss = session.query(models.Neighborhood).get(id)
        session.begin(subtransactions=True)
        try:
            session.delete(ss)
            session.commit()
        except Exception, e:
            session.rollback()
            raise Exception(e)
        return True

    def vlan_list(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def vlan_create(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def vlan_info(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def vlan_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def vlan_delete(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_list(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_create(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_info(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def subnet_delete(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def ip_list(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def ip_create(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def ip_info(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def ip_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def ip_delete(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_list(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_create(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_info(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_update(self, *args, **kwargs):
        raise FeatureNotImplemented()

    def policy_delete(self, *args, **kwargs):
        raise FeatureNotImplemented()
