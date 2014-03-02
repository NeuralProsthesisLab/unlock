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


class Builder(object):
    def __init__(self, platform):
        super(Builder, self).__init__()
        self.platform = str(platform).casefold()

    def build(self):
        ret = {
            'win32'.casefold(): builder.build_windows,
            'darwin'.casefold(): builder.build_darwin,
            'linux'.casefold(): builder.build_linux
        }.get(self.platform, builder.unsupported)()
        return ret

    def build_windows(self):

        conf = None
        logger = None
        loglevel = logging.INFO

        args = None
        options = None
        parser = None

        usage = "usage: %prog [options]"
        python = 'C:\Python27\python.exe'
        scons = 'C:\Python27\Scripts\scons-2.3.0.py'
        lib_dir = os.path.join('lib', 'win-x86-msvc-10')
        runtime_dir = os.path.join('..', 'acquire')
        cwd = os.getcwd()

        runtime_dir_help = 'sets the installation directory; defaults to ..\acquire'
        lib_dir_help = 'sets the library directory to copy binaries to; default is lib\win-x86-msvc-10, relative the build directory'
        clean_help = 'removes old binaries before building'
        python_help = 'specifies the location of the python interpreter; default is c:\Python27\python.exe'
        scons_help = 'specifies the location of the scons script; default is c:\Python27\Scripts\scons-2.3.0.py'
        setup_help = 'configures the build environment for the first time; must be run with the first build'
        build_help = 'builds the libraries and tests and copies them to the library directory'
        parser = OptionParser(version="%prog 1.0", usage=usage)

        parser.add_option('-n', '--runtime-dir', dest='runtime_dir', action='store_true', default=False,
            metavar='RUNTIME_DIR', help=runtime_dir_help)
        parser.add_option('-p', '--python', dest='python', action='store_true', default=False, metavar='PYTHON',
            help=python_help)
        parser.add_option('-o', '--scons', dest='scons', action='store_true', default=False, metavar='SCONS',
            help=scons_help)
        parser.add_option('-l', '--lib-dir', dest='lib_dir', action='store_true', default=False, metavar='LIB_DIR',
            help=lib_dir_help)
        parser.add_option('-c', '--clean', dest='clean', action='store_true', default=False, metavar='CLEAN',
            help=clean_help)
        parser.add_option('-s', '--setup', dest='setup', action='store_true', default=False, metavar='SETUP',
            help=setup_help)
        parser.add_option('-i', '--install', dest='install', action='store_true', default=False, metavar='install',
            help=setup_help)
        parser.add_option('-b', '--build', dest='build', action='store_true', default=False, metavar='build',
            help=build_help)
        (options, args) = parser.parse_args()

        redirect = {'stdin': sys.stdin, 'stdout': sys.stdout, 'stderr': sys.stderr}

        if options.setup:
            setup_command = ['tar', 'xzvf', 'includes.tar.gz']
            subprocess.check_call(setup_command, **redirect)

        if options.python:
            python = options.python

        if options.scons:
            scons = options.scons

        if options.clean:
            subprocess.check_call([python, scons, '-c'], **redirect)

        if options.lib_dir:
            lib_dir = options.lib_dir

        if options.build:
            subprocess.check_call([python, scons, '-Q'], **redirect)

            ns_dll = 'neuralsignal_win_x86.dll'
            ns_test_dll = 'neuralsignal-unit-tests.exe'
            ns = os.path.join(cwd, ns_dll)
            ns_dest = os.path.join(cwd, lib_dir, ns_dll)

            ns_dest_python = os.path.join(cwd, lib_dir, 'neuralsignal.pyd')
            ns_test = os.path.join(cwd, ns_test_dll)
            ns_test_dest = os.path.join(cwd, lib_dir, ns_test_dll)

            build_command = ['cp', ns, ns_dest]
            build_command1 = ['cp', ns, ns_dest_python]
            build_command2 = ['cp', ns_test, ns_test_dest]

            # execute the commands
            subprocess.check_call(build_command, **redirect)
            subprocess.check_call(build_command1, **redirect)
            subprocess.check_call(build_command2, **redirect)

        if options.runtime_dir:
            runtime_dir = options.runtime_dir

        if options.install:
            def install_file(file_name):
                libs = os.path.join(cwd, lib_dir, file_name)
                dest = os.path.join(cwd, runtime_dir, file_name)
                install_command = ['cp', libs, dest]
                subprocess.check_call(install_command, **redirect)

            for root, dirs, files in os.walk(os.path.join(cwd, lib_dir), topdown=False):
                for file in files:
                    if file.endswith('dll') or file.endswith('exe') or file.endswith('pyd'):
                        install_file(file)

    def unsupported(self):
        raise RuntimeError('Unsupported OS '+ self.platform)

    def build_linux(self):
        return self.unsupported()

    def build_darwin(self):
        return self.unsupported()


if __name__ == '__main__':
    builder = Builder(sys.platform)
    builder.build()
