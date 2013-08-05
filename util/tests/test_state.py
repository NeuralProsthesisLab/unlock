from unlock.util import RunState, TrialTimeState, TrialState

import time
import unittest

class StateTests(unittest.TestCase):
        
    def testRunState(self):
        run_state = RunState()
        self.assertEquals(RunState.stopped, run_state.state)
        self.assertEquals(True, run_state.is_stopped())
        self.assertEquals(False, run_state.is_running())
        self.assertEquals(False, run_state.is_resting())

        run_state.run()
        self.assertEquals(RunState.running, run_state.state)
        self.assertEquals(False, run_state.is_stopped())
        self.assertEquals(True, run_state.is_running())
        self.assertEquals(False, run_state.is_resting())
        
        run_state.rest()
        self.assertEquals(RunState.resting, run_state.state)
        self.assertEquals(False, run_state.is_stopped())
        self.assertEquals(False, run_state.is_running())
        self.assertEquals(True, run_state.is_resting())
        
        run_state.run()
        self.assertEquals(RunState.running, run_state.state)
        self.assertEquals(False, run_state.is_stopped())
        self.assertEquals(True, run_state.is_running())
        self.assertEquals(False, run_state.is_resting())
                
        run_state.stop()
        self.assertEquals(RunState.stopped, run_state.state)
        self.assertEquals(True, run_state.is_stopped())
        self.assertEquals(False, run_state.is_running())
        self.assertEquals(False, run_state.is_resting())
            
    
    def testTrialTimeState(self):
        trial_time_state = TrialTimeState(1.0, 1.0)
        trial_time_state.begin_trial()
        self.assertFalse(trial_time_state.is_trial_complete())
        start = time.time()
        trial_time_state.update_trial_time(.01)
        self.assertFalse(trial_time_state.is_trial_complete())
        
        time.sleep(.5)
        delta = time.time() - start
        trial_time_state.update_trial_time(delta)
        self.assertFalse(trial_time_state.is_trial_complete())
        
        time.sleep(.58)
        delta = time.time() - (start + delta)
        trial_time_state.update_trial_time(delta)
        self.assertTrue(trial_time_state.is_trial_complete())
        
        time.sleep(.3)
        delta = time.time() - (start + delta)        
        trial_time_state.update_trial_time(delta)
        self.assertFalse(trial_time_state.is_rest_complete())
        
        time.sleep(.5)
        delta = time.time() - (start + delta)        
        trial_time_state.update_trial_time(delta)
        self.assertTrue(trial_time_state.is_rest_complete())                
        
    def testTrialState(self):
        trial_state = TrialState.create(1.0, 1.0)
        trial_state.start()
        start = time.time()
        state, change = trial_state.update_state(0)
        self.assertEquals(RunState.running, state)
        self.assertEquals(TrialState.unchanged, change)
        
        
def getSuite():
    return unittest.makeSuite(StateTests,'test')

if __name__ == "__main__":
    unittest.main()
    
    