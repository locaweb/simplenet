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
# @author: Francisco Freire, Locaweb.
# @author: Thiago Morello (morellon), Locaweb.
# @author: Willian Molinari (PotHix), Locaweb.
# @author: Juliano Martinez (ncode), Locaweb.
# @author: Luiz Ozaki, Locaweb.

import ConfigParser
import inspect
import os
import socket
import logging

caller = inspect.stack()[-1][1].split('/')[-1]
config = ConfigParser.ConfigParser()
config_file = "/etc/simplenet/simplenet.cfg"
logger = None

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

if os.path.isfile(config_file):
    config.read(config_file)

class StdOutAndErrWapper(object):
    def write(self, data):
        logger.info("[bottle] " + str(data).strip())

def stdout_logger():
    global logger
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(LOGGING_LEVELS.get(config.get("logging", "level").lower()))

def get_logger():
    global logger
    if logger: return logger
    formatter = logging.Formatter('%(asctime)s [%(name)s/%(levelname)s] %(message)s')

    logger = logging.getLogger('simplenet-server')
    log_file = config.get("logging", "file")
    log_level = LOGGING_LEVELS.get(config.get("logging", "level").lower())

    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(formatter)

    logger.setLevel(log_level)
    fileHandler.setLevel(log_level)

    logger.addHandler(fileHandler)

    return logger

def section(cfg, cfg_section):
    r = {}
    for k in cfg.options(cfg_section):
        r[k] = cfg.get(cfg_section, k)
    return(r)

def get_rolesdb():
    cfg = ConfigParser.ConfigParser()
    cfg.read(config_file)
    roles = section(cfg, "roles")
    roles["ro"] = filter(None, [u.strip() for u in roles["ro"].split(",")])
    roles["rw"] = filter(None, [u.strip() for u in roles["rw"].split(",")])
    roles["ro"].extend(roles["rw"])
    return roles
