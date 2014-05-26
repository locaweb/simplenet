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
import syslog

caller = inspect.stack()[-1][1].split('/')[-1]
config = ConfigParser.ConfigParser()
config_file = "/etc/simplenet/simplenet.cfg"
logger = None

if os.path.isfile(config_file):
    config.read(config_file)

class StdOutAndErrWapper(object):
    def write(self, data):
        if '\n' in data:
            for line in data.split('\n'):
                logger.info(line)
        else:
            logger.info(str(data).strip())

class SyslogWrapper(object):

    def __init__(self, config=None):
        self.config = config

    def info(self, msg):
        syslog.syslog(syslog.LOG_INFO, msg)

    def warning(self, msg):
        syslog.syslog(syslog.LOG_WARNING, msg)

    def critical(self, msg):
        syslog.syslog(syslog.LOG_CRIT, msg)

    def error(self, msg):
        syslog.syslog(syslog.LOG_ERR, msg)

    def debug(self, msg):
        if self.config.has_section('server') and \
           self.config.getboolean('server', 'debug'):
            syslog.syslog(syslog.LOG_DEBUG, msg)


def get_logger():
    global logger
    global config
    if logger: return logger
    syslog.openlog(caller, syslog.LOG_PID, syslog.LOG_DAEMON)
    logger = SyslogWrapper(config)
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
