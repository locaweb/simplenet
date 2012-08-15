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
from simplenet.exceptions import EntityNotFound, OperationNotPermited
from simplenet.network_appliances.base import SimpleNet
from sqlalchemy.exc import IntegrityError

LOG = logging.getLogger(__name__)
session = db_utils.get_database_session()


class Net(SimpleNet):

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
