from distutils.core import setup
import os
#import py2exe

def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def walk_dirs(dirs):
    packages, package_data = [], {}
    for package_dir in dirs:
        for dirpath, dirnames, filenames in os.walk(package_dir):
            dirnames[:] = [d for d in dirnames]
            parts = fullsplit(dirpath)
            package_name = '.'.join(parts)
            if '__init__.py' in filenames:
                packages.append(package_name)
            elif filenames:
                relative_path = []
                while '.'.join(parts) not in packages:
                    part = parts.pop()
                    print 'parts...', part
                    relative_path.append(part)
                relative_path.reverse()
                path = os.path.join(*relative_path)
                package_files = package_data.setdefault('.'.join(parts), [])
                package_files.extend([os.path.join(path, f) for f in filenames])
    return packages, package_data

packages, package_data = walk_dirs(['core', 'apps', 'examples'])
setup(name='unlock',
      version='0.3.7',
      packages=packages,
      package_data=package_data,
      maintainer='James Percent',
      maintainer_email='james@syndeticlogic.net',
      )
