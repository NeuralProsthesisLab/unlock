
from .. import ApplicationContext, XMLConfig, PythonConfig, Object
from unlock.util import TrialTimeState, RunState, TrialState
import context

import time
import unittest
import unlock
import inspect
import os


class TrialStateFactory(PythonConfig):
    def __init__(self):
        super(TrialStateFactory, self).__init__()
        
    @Object(context.PROTOTYPE)
    def RunState(self):
        return unlock.util.RunState()
            
    @Object(context.PROTOTYPE)
    def TrialTimeState(self):
        return TrialTimeState(trial_duration=1.0, rest_duration=1.0)
            
    @Object(context.PROTOTYPE)
    def TrialState(self):
        return TrialState.create(1.0, 1.0)

    @Object(context.PROTOTYPE)
    def TrialState1(self):
        return TrialState(self.TrialState(), self.RunState())

    def NotExposed(self):
        pass
        
        
class ContextTests(unittest.TestCase):
    def testPythonApplicationContext(self):
        
        app_ctx = ApplicationContext(TrialStateFactory())
     
        trial_state = app_ctx.get_object("TrialState")
        trial_state1 = app_ctx.get_object("TrialState1")
        trial_state.start()
        start = time.time()
        state, change = trial_state.update_state(0)
        self.assertEquals(unlock.util.RunState.running, state)
        self.assertEquals(unlock.util.TrialState.unchanged, change)
        self.assertEquals(1.0, trial_state.time_state.trial_duration)
        self.assertEquals(1.0, trial_state.time_state.rest_duration)                
    
    def testApplicationContext(self):        
        app_ctx_xml = os.path.join(os.path.dirname(inspect.getfile(ContextTests)), "app-ctx.xml")
        app_ctx = ApplicationContext(XMLConfig(config_location = app_ctx_xml))
     
     
        trial_state = app_ctx.get_object("trial_state")
        trial_state1 = app_ctx.get_object("trial_state1")        
        trial_state.start()
        start = time.time()
        state, change = trial_state.update_state(0)
        self.assertEquals(unlock.util.RunState.running, state)
        self.assertEquals(unlock.util.TrialState.unchanged, change)
        self.assertEquals(1.0, trial_state.time_state.trial_duration)
        self.assertEquals(1.0, trial_state.time_state.rest_duration)        
            
            
def getSuite():
    return unittest.makeSuite(ContextTests,'test')

if __name__ == "__main__":
    unittest.main()
    