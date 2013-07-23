

class UnlockModel(object):
    def __init__(self, state=None):
        super(UnlockModel, self).__init__()
        self.state = state
        
    def start(self):
        pass
        
    def stop(self):
        pass
        
    def get_state(self):
        return self.state
        
        
class AlternatingBinaryStateModel(UnlockModel):
    def __init__(self, hold_duration=300):
        self.hold_duration = hold_duration
        self.state = True
        self.count = 0
        
    def get_state(self):
        ret = self.state
        self.count += 1
        if self.count % self.hold_duration == 0:
            self.state = not self.state
        return ret
            
           
    