from distutils.core import setup
import os
import shutil

ignore_files = ['boost_1_54_0.tar.bz2', 'boost_1_54_0.zip', 'boost-win.exe', 'boost-nx.sh', 'candidate_view_code']
ignore_dirs = ['bci/boost/include', 'view/candidate_view_code']
prefix = 'unlock'
def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def ignore_file(file_name):
    for ignore_prefix in ignore_files:
        if file_name.startswith(ignore_prefix):
            return True
    return False
    
def walk_dirs(dirs):
    packages, package_data = [], {}
    for package_dir in dirs:
        for dirpath, dirnames, filenames in os.walk(package_dir):
            ignoredir = False
            for ignore_dir in ignore_dirs:
                if dirpath.startswith(ignore_dir):
                    ignoredir=True
                    
            if ignoredir:
                continue
            
            import time
            time.sleep(.24)
            dirnames[:] = [d for d in dirnames]
            parts = fullsplit(dirpath)
            package_name = '.'.join(parts)

            if '__init__.py' in filenames:
                packages.append(package_name)
            elif filenames:
                print filenames
                relative_path = []
                while '.'.join(parts) not in packages:
                    print 'parts ', parts, packages
                    if len(parts) > 0:
                        top = parts.pop()
                        print 'top = ', top
                        if not ignore_file(top):
                            print 'adding top = ', top
                            relative_path.append(top)
                    else:
                        break
                    
                relative_path.reverse()
                print 'relative_path = ', relative_path
               # if len(relative_path) > 0:
                path = os.path.join(*relative_path)
                package_files = package_data.setdefault('.'.join(parts), [])
                package_files.extend([os.path.join(path, f) for f in filenames])
                    
    return packages, package_data


#packages, package_data = walk_dirs(['controller', 'context', 'model', 'util', 'view']) #'neural', 'util', 'view'])

#                                    , 'model', 'bci', 'context', 'controller', 'unlock.py', 'conf.json', '__init__.py'])

#print package_data

packages = ['unlock', 
            'unlock.context', 'unlock.context.test',
            'unlock.controller', 'unlock.controller.test', 
            'unlock.model', 'unlock.model.test',
            'unlock.neural', 'unlock.neural.acquire', 
            'unlock.util', 'unlock.util.test',
            'unlock.view', 'unlock.view.test']



package_data = {
                'unlock' : ['conf.json', 'README.md'],
                'unlock.controller' : ['resource/analyzer.jpg', 'resource/Arrow.png', 'resource/ArrowSel.png', 'resource/emg-100x100.jpg', 'resource/emg.jpg', 'resource/IRCodes.txt', 'resource/LazerToggle.png', 'resource/LazerToggleS.png', 'resource/rsz_analyzer.jpg', 'resource/scope.png', 'resource/tv.png'],
                'unlock.context.test' : ['app-ctx.xml'], 
                 'unlock.model' : [],
# win-x86 libs find acquire-c++/boost/win-x86/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/
                'unlock.neural' : ['acquire-c++/boost/win-x86/lib/boost_atomic-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_chrono-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_context-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_date_time-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_filesystem-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_graph-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_iostreams-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_locale-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_log-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_log_setup-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_c99-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_c99f-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_c99l-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_tr1-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_tr1f-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_math_tr1l-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_prg_exec_monitor-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_program_options-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_python-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_random-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_regex-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_serialization-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_signals-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_system-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_thread-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_timer-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_unit_test_framework-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_wave-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/boost_wserialization-vc110-mt-1_54.dll',
                            'acquire-c++/boost/win-x86/lib/signal-unit-tests.exe',
                            'acquire-c++/boost/win-x86/lib/signal-unit-tests.exp',
                            'acquire-c++/boost/win-x86/lib/signal.pyd',
                            'acquire-c++/boost/win-x86/lib/signal_win_x86.dll',
# mac os x libs find acquire-c++/boost/macosx-x86-64/lib | grep -v -e lib$  -e gd | sed s/^/\'/ | sed s/$/\',/ 
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_prg_exec_monitor.a',
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_python.a',
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_system.a',
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_test_exec_monitor.a',
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_thread.a',
                            'acquire-c++/boost/macosx-x86-64/lib/libboost_unit_test_framework.a',
                            'acquire-c++/boost/macosx-x86-64/lib/signal_darwin_x86_64.so'],
                 'unlock.view' : ['bell-ring-01.mp3', 'unlock.png']}
#for i in range(len(packages)):
#    packages[i] = 'unlock.'+packages[i]
    
#packages.append('unlock')
    
print packages

print 88*'-'
print 88*'-'
print 88*'-'
#print package_data
import sys
#sys.exit(0)

setup(name='unlock', version='0.3.7', packages=packages, package_data=package_data,
      author='James Percent', author_email='james@shift5.net')
