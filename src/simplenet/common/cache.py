#!/usr/bin/python
# -*- coding: utf-8; -*-
#
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
# @author: Eduardo S. Scarpellini
# @author: Luiz Ozaki


__copyright__ = "Copyright 2012, Locaweb IDC"


import redis
from simplenet.common.config import config


__all__ = ["RedisClient"]


class RedisClient(object):
    def __init__(self, timeout=3, db=2):
        self.host = config.get("redis", "host")
        self.port = config.getint("redis", "port")
        self._redis   = redis.Redis(host=self.host, port=self.port, db=db,
                                    socket_timeout=timeout)

    def get_connection(self):
        if self._redis is None or not self._redis.ping():
            self._redis = redis.Redis(host=self.host, port=self.port,
                                      socket_timeout=self.timeout)
        return self._redis
