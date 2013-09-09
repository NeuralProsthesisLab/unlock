from distutils.core import setup
import os
import shutil

packages = ['unlock', 
            'unlock.context', 'unlock.context.test',
            'unlock.controller', 'unlock.controller.test', 
            'unlock.model', 'unlock.model.test',
            'unlock.neural', 'unlock.neural.acquire', 'unlock.neural.classify', 
            'unlock.util', 'unlock.util.test',
            'unlock.view', 'unlock.view.test']

package_data = {
                'unlock' : ['conf.json', 'README.md'],
                'unlock.controller' : ['resource/analyzer.jpg', 'resource/Arrow.png', 'resource/ArrowSel.png', 'resource/emg-100x100.jpg',
                                       'resource/emg.jpg', 'resource/IRCodes.txt', 'resource/LazerToggle.png', 'resource/LazerToggleS.png',
                                       'resource/rsz_analyzer.jpg', 'resource/scope.png', 'resource/tv.png'],
                'unlock.context.test' : ['app-ctx.xml'], 
                 'unlock.model' : [],

# win-x86 libs find acquire-c++/boost/win-x86/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/
                'unlock.neural' : ['acquire/boost_atomic-vc100-mt-1_54.dll', 'acquire/boost_chrono-vc100-mt-1_54.dll',
                                   'acquire/boost_date_time-vc100-mt-1_54.dll', 'acquire/boost_python3-vc100-mt-1_54.dll',
                                   'acquire/boost_random-vc100-mt-1_54.dll', 'acquire/boost_system-vc100-mt-1_54.dll',
                                   'acquire/boost_thread-vc100-mt-1_54.dll', 'acquire/boost_unit_test_framework-vc100-mt-1_54.dll',
                                   'acquire/Enobio3GAPI.dll', 'acquire/QtCore4.dll', 'acquire/WinBluetoothAPI.dll',
                                   'acquire/msvcr100.dll', 'acquire/msvcp100.dll', 'acquire/python33.dll',
                                   'acquire/neuralsignal-unit-tests.exe', 'acquire/neuralsignal.pyd',

# mac os x libs find acquire-c++/boost/macosx-x86-64/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/ 
                            #'acquire/neuralsignal.so'
                            ],
                 'unlock.view' : ['bell-ring-01.mp3', 'unlock.png']}

setup(name='unlock', version='0.3.7', packages=packages, package_data=package_data,
      author='James Percent', author_email='james@shift5.net')
