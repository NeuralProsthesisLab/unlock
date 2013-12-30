# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
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

from distutils.core import setup
import os
import shutil

packages = ['unlock', 
            'unlock.context', 'unlock.context.test',
            'unlock.controller', 'unlock.controller.test', 
            'unlock.state', 'unlock.state.test',
            'unlock.decode', 'unlock.decode.acquire', 'unlock.decode.classify', 
            'unlock.util', 'unlock.util.test',
            'unlock.view', 'unlock.view.test']

package_data = {
                'unlock' : ['conf.json', 'README.md'],
                'unlock.controller' : ['resource/analyzer.jpg', 'resource/Arrow.png', 'resource/ArrowSel.png', 'resource/emg-100x100.jpg',
                                       'resource/emg.jpg', 'resource/IRCodes.txt', 'resource/LazerToggle.png', 'resource/LazerToggleS.png',
                                       'resource/rsz_analyzer.jpg', 'resource/scope.png', 'resource/tv.png'],
                'unlock.context.test' : ['app-ctx.xml'], 
                 'unlock.state' : [],
# win-x86 libs find acquire-c++/boost/win-x86/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/
                'unlock.decode' : ['acquire/boost_atomic-vc100-mt-1_54.dll', 'acquire/boost_chrono-vc100-mt-1_54.dll',
                                   'acquire/boost_date_time-vc100-mt-1_54.dll', 'acquire/boost_python3-vc100-mt-1_54.dll',
                                   'acquire/boost_random-vc100-mt-1_54.dll', 'acquire/boost_system-vc100-mt-1_54.dll',
                                   'acquire/boost_thread-vc100-mt-1_54.dll', 'acquire/boost_unit_test_framework-vc100-mt-1_54.dll',
                                   'acquire/Enobio3GAPI.dll', 'acquire/QtCore4.dll', 'acquire/WinBluetoothAPI.dll',
                                   'acquire/msvcr100.dll', 'acquire/msvcp100.dll', 'acquire/python33.dll',
                                   'acquire/neuralsignal-unit-tests.exe', 'acquire/neuralsignal.pyd',
                                   'acquire/gMOBIlabplus.dll'
# mac os x libs find acquire-c++/boost/macosx-x86-64/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/ 
                            #'acquire/neuralsignal.so'
                            ],
                 'unlock.view' : ['bell-ring-01.mp3', 'unlock.png',
                                  'resource/Female/sounds/alone.wav', 'resource/Female/sounds/bored.wav',
                                  'resource/Female/sounds/down.wav', 'resource/Female/sounds/explain.wav',
                                  'resource/Female/sounds/get.wav', 'resource/Female/sounds/goodbye.wav',
                                  'resource/Female/sounds/hello.wav', 'resource/Female/sounds/help.wav',
                                  'resource/Female/sounds/howareyou.wav', 'resource/Female/sounds/hungry.wav',
                                  'resource/Female/sounds/left.wav', 'resource/Female/sounds/move.wav',
                                  'resource/Female/sounds/no.wav', 'resource/Female/sounds/nose.wav',
                                  'resource/Female/sounds/pain.wav', 'resource/Female/sounds/repeat.wav',
                                  'resource/Female/sounds/right.wav', 'resource/Female/sounds/sorry.wav',
                                  'resource/Female/sounds/thanks.wav', 'resource/Female/sounds/thirsty.wav',
                                  'resource/Female/sounds/up.wav', 'resource/Female/sounds/when.wav',
                                  'resource/Female/sounds/where.wav', 'resource/Female/sounds/who.wav',
                                  'resource/Female/sounds/yes.wav',
                                  
                                  'resource/Male/sounds/alone.wav', 'resource/Male/sounds/bored.wav',
                                  'resource/Male/sounds/down.wav', 'resource/Male/sounds/explain.wav',
                                  'resource/Male/sounds/get.wav', 'resource/Male/sounds/goodbye.wav',
                                  'resource/Male/sounds/hello.wav', 'resource/Male/sounds/help.wav',
                                  'resource/Male/sounds/howareyou.wav', 'resource/Male/sounds/hungry.wav',
                                  'resource/Male/sounds/left.wav', 'resource/Male/sounds/move.wav',
                                  'resource/Male/sounds/no.wav', 'resource/Male/sounds/nose.wav',
                                  'resource/Male/sounds/pain.wav', 'resource/Male/sounds/repeat.wav',
                                  'resource/Male/sounds/right.wav', 'resource/Male/sounds/sorry.wav',
                                  'resource/Male/sounds/thanks.wav', 'resource/Male/sounds/thirsty.wav',
                                  'resource/Male/sounds/up.wav', 'resource/Male/sounds/when.wav',
                                  'resource/Male/sounds/where.wav', 'resource/Male/sounds/who.wav',
                                  'resource/Male/sounds/yes.wav'
                                  ]}
                                
setup(name='unlock', version='0.3.7', packages=packages, package_data=package_data,
      author='James Percent', author_email='james@shift5.net')
