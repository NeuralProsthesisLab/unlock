# Copyright (c) James Percent and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from functools import wraps
from flask import request, Response, render_template, url_for
from admin import app
from admin import database
from sqlalchemy import create_engine
from unlock import unlock_runtime
from subprocess import Popen

class UnlockRunner(object):
    def __init__(self, python_path='c:\\Python33\\python.exe',
            unlock_runtime_path='../unlock_runtime.py', *args): #=['-c', '../ssvep-diag.json']):
        
        super(UnlockRunner, self).__init__()
        self.python_path = python_path
        self.unlock_runtime_path = unlock_runtime_path
        self.args = args
        self.p = None
        print 'args ', args, ' *args '
    def start(self):
        popen_args = [self.python_path, self.unlock_runtime_path, self.args] #'-c', '../ssvep-diag.json'])
        popen_args.expand(args)
        print("popen args  = ", popen_args)
        self.p = Popen(popen_args) #'-c', '../ssvep-diag.json'])
    def wait(self, ):
        assert self.p is not None
        self.p.wait()
        self.p = None
    
    


@app.route('/unlock-ssvep-diag')
def start():
    try:
#        print("params = ", request.args)
        dbConnection = database.create_engine()
#        if request.args.get('conf')
        runner = UnlockRunner(args=['-c', '../ssvep-diag.json'])
        runner.start()
        runner.wait()
        return render_template('unlock.html')
    except Exception as e:
        print("Exception = ", dir(e), e, e.__doc__)
        return e.__doc__
