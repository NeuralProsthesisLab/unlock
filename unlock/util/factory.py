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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.import socket

__author__ = 'jpercent'

class AbstractFactory(object):
    def __init__(self):
        super(AbstractFactory, self).__init__()

    def create_singleton(self, type_name, attr_name, config):
        #print('atter name = ', attr_name)
        assert not hasattr(self, attr_name)
        args = config[attr_name].get('args', None)
        if args:
            newobj = getattr(self, type_name)(**args)
        else:
            newobj = getattr(self, type_name)()

        if newobj is None:
            self.logger.error("UnlockFactory.create_singleton returned None; objdesc = ", type_name)

        setattr(self, attr_name, newobj)
        assert newobj
        return newobj

    def create(self, type_name, config):
        objdesc = config[type_name]
        deps = None
        args = None

        if 'args' in objdesc:
            args = objdesc['args']

        if 'deps' in objdesc:
            #print("typename = ", type_name, objdesc)
            deps = {}

            for key, value in objdesc['deps'].items():
                if type(value) == list:
                    depobj = []
                    for element in value:
                        depobj.append(self.create(element, config))
                else:
                    depobj = self.create(value, config)

                deps[key] = depobj

            if args and deps:
                args.update(deps)
            elif deps.keys():
                assert not args
                args = deps

        if args:
            newobj = getattr(self, type_name)(**args)
        else:
            newobj = getattr(self, type_name)()

        if newobj is None:
            self.logger.error("UnlockFactory.create_"+str(type_name), "returned None; objdesc = ", objdesc)

        assert newobj
        return newobj
