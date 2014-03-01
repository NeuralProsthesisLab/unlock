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
from optparse import OptionParser
import subprocess
import logging
import inspect
import sys
import os

def build_windows():
    conf = None
    logger = None
    loglevel = logging.INFO

    args = None
    options = None
    parser = None
    usage = "usage: %prog [options]"

    python = 'C:\Python27\python.exe'
    scons = 'C:\Python27\Scripts\scons-2.3.0.py'
    lib_dir = 'lib\win-x86-msvc-10'
    cwd = os.path.dirname(inspect.getfile(build_windows))

    lib_dir_help = 'sets the library directory to copy binaries to; default is lib\win-x86-msvc-10, relative the build directory'
    clean_help = 'removes old binaries before building'
    python_help = 'specifies the location of the python interpreter; default is c:\Python27\python.exe'
    scons_help = 'specifies the location of the scons script; default is c:\Python27\Scripts\scons-2.3.0.py'
    setup_help = 'configures the build environment for the first time; must be run with the first build'

    parser = OptionParser(version="%prog 1.0", usage=usage)
    parser.add_option('-l', '--libdir', dest='lib_dir', action='store_true', default=False, metavar='LIB_DIR', help=lib_dir_help)
    parser.add_option('-c', '--clean', dest='clean', action='store_true', default=False, metavar='CLEAN', help=clean_help)
    parser.add_option('-s', '--setup', dest='setup', action='store_true', default=False, metavar='SETUP', help=setup_help)
    parser.add_option('-s', '--setup', dest='setup', action='store_true', default=False, metavar='SETUP', help=setup_help)
    parser.add_option('-i', '--install', dest='install', action='store_true', default=False, metavar='install', help=setup_help)
    (options, args) = parser.parse_args()

    redirect = {'stdin': sys.stdin, 'stdout': sys.stdout, 'stderr': sys.stderr}

    if options.setup:
        command = ['tar', 'xzvf', 'includes.tar.gz']
        subprocess.check_call(command, **redirect)

    if options.clean:
        subprocess.check_call([python, scons, '-c'], **redirect)

    if options.lib_dir:
        lib_dir = options.lib_dir

    if options.build:
        # build it
        subprocess.check_call([python, scons, '-Q'], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

        # copy to the libdir directory
        # setup the file names
        ns_dll = 'neuralsignal_win_x86.dll'
        ns_test_dll = 'neuralsignal-unit-tests.exe'
        ns = os.path.join(cwd, ns_dll)
        ns_dest = os.path.join(cwd, lib_dir, ns_dll)
        # python runtime won't find it on windows, if it is not named .pyd
        ns_dest_python = os.path.join(cwd, lib_dir, 'neuralsignal.pyd')
        ns_test = os.path.join(cwd, ns_test_dll)
        ns_test_dest = os.path.join(cwd, lib_dir, ns_test_dll)

        # construct the command lists
        command = ['cp', ns, ns_dest]
        command1 = ['cp', ns, ns_dest_python]
        command2 = ['cp', ns_test, ns_test_dest]

        # execute the commands
        subprocess.check_call(command, **redirect)
        subprocess.check_call(command1, **redirect)
        subprocess.check_call(command2, **redirect)

    if options.install:
        # copy boost
        pass
    #   cp neuralsignal_win_x86.dll neuralsignal-unit-tests.exe ../acquire
    #   cp boost/win-x86-msvc-10/lib/boost_*.dll ../acquire
    #   cp neuralsignal_win_x86.dll ../acquire/neuralsignal.pyd
    #   cp boost/win-x86-msvc-10/lib/Enobio3GAPI.dll boost/win-x86-msvc-10/lib/QtCore4.dll boost/win-x86-msvc-10/lib/WinBlueToothAPI.dll ../acquire
    #   cd boost/win-x86-msvc-10/lib
    #   subprocess.check_call([python, scons, '-Q'], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


if __name__ == '__main__':
    build_windows()



