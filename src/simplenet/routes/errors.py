#!/usr/bin/python

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

from bottle import error, request, response

from simplenet.common.config import get_logger
from simplenet.common.http_utils import reply_json

logger = get_logger()

@error(400)
@reply_json
def error400(err):
    return {"status": err.status, "message": err.output}


@error(403)
@reply_json
def error403(err):
    return {"status": err.status, "message": err.output}


@error(404)
@reply_json
def error404(err):
    return {"status": err.status, "message": err.output}


@error(405)
@reply_json
def error405(err):
    return {"status": err.status, "message": err.output}


@error(500)
@reply_json
def error500(err):
    if err.exception is not None:
        return {"status": err.status, "message": err.exception.__repr__()}
    else:
        return {"status": err.status, "message": err.output}


@error(501)
@reply_json
def error501(err):
    return {"status": err.status, "message": err.output}
