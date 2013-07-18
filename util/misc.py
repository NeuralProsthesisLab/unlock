import inspect
import os
    
class Trigger(object):
    NoValue=-1
    Start=0
    Stop=1
    Pause=3
    Cue=4
    Indication=5
    Reset=6
    UsageDefined=7
    UsageDefined1=7
    UsageDefined2=7
    
    def __init__(self, log_triggers=False, store_triggers=False):
        self.value = 0
        if log_triggers:
            self.log = logging.getLogger(__name__)
    def send(self, value):
        self.value = value 
        return
    def value(self):
        val = self.trigger
        self.trigger = 0
        return val
        
               
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
            
 