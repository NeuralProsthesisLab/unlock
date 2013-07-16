import inspect
import os
            
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
            
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
           
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
            
            
class Resource(object):
    def __init__(self, path=None):
        if path == None:
            #os.path.dirname(inspect.getabsfile(unlock.Resource))
            self.path = os.path.dirname(inspect.getfile(Resource))+'/resource/'
        else:                
            self.path = path
        self.resources = []
        
    def reset_path(self, path):
        self.path = path
        
    def add_resource(self, resource):
        self.resources.append(resource)
            
 