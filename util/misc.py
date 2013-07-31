import inspect
import os


class DelegatorMixin(object):
    def __init__(self):
        super(DelegatorMixin, self).__init__()
        self.delegates = set([])
        self.ordering = []
        
    def __getattr__(self, name):
        for delegate in self.ordering:
            try:
                return getattr(delegate, name)
            except:
                pass
        raise AttributeError(name)
            
    def add_delegate(self, delegate):
        if not delegate in self.delegates:
            self.delegates.add(delegate)
            self.ordering.append(delegate)
            
          
class Trigger(object):
    Null=0
    Start=1
    Stop=2
    Pause=3
    Cue=4
    Indicate=5
    Rest=6
    Up=7
    Right=8
    Down=9
    Left=10
    Complete=11
    UsageDefined=12
    UsageDefined1=13
    UsageDefined2=14
        
        
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
            
            