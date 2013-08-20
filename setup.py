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


packages, package_data = walk_dirs(['util', 'view', 'model', 'bci', 'context', 'controller', 'unlock.py', 'conf.json', '__init__.py'])

packages = ['unlock',
            'unlock.bci'
            'unlock.context', 'unlock.context.test',
            'unlock.', 'unlock.', 'unlock.', 'unlock.', 'unlock.', 'unlock.'
            'unlock.util', 'unlock.util.tests',
            'unlock.', 'unlock.', 'unlock.', 'unlock.', 'unlock.', 'unlock.'
            'unlock.util', 'unlock.',

            ]

for i in range(len(packages)):
    packages[i] = 'unlock.'+packages[i]
    
packages.append('unlock')
    
print packages

print 88*'-'
print 88*'-'
print 88*'-'
print package_data
import sys
sys.exit(0)

setup(name='unlock', version='0.3.7', packages=packages, package_data=package_data, author='James Percent',
      author_email='james@shift5.net', maintainer='James Percent', maintainer_email='james@shift5.net')
