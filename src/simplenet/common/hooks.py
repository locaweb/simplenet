# Copyright 2013 Locaweb.
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

import os
from functools import wraps

def pre_run(f):
    @wraps(f)
    def pre(*args, **kwargs):
        if os.path.isfile("/etc/simplenet/hooks/pre_%s.py" % f.__name__):
            ## run the hook
            return f(*args, **kwargs)
        return f(*args, **kwargs)
    return pre

def post_run(f):
    @wraps(f)
    def post(*args, **kwargs):
        if os.path.isfile("/etc/simplenet/hooks/post_%s.py" % f.__name__):
            result = f(*args, **kwargs)
            ## run the hook 
            return result
        return f(*args, **kwargs)
    return post