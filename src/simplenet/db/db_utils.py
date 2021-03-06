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
# @author: Luiz Ozaki, Locaweb.

from sqlalchemy.orm import sessionmaker
from simplenet.db import models
from simplenet.common.config import get_logger

logger = get_logger()

_engine = models.engine
_maker = None

def get_database_session(autocommit=True, expire_on_commit=True):
    global _maker, _engine
    if not _maker:
        assert _engine
        _maker = sessionmaker(bind=_engine,
                              autocommit=autocommit,
                              expire_on_commit=expire_on_commit)
    return _maker()

def unregister_database_models(base):
    global _engine
    assert _engine
    base.metadata.drop_all(_engine)
