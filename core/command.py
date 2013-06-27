
class BaseCommand(object):
    def __init__(self, delta, decision, selection):
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.data = data
        
class CommandReceiver(object):
    def get_next_command(self):
        raise NotImplementedError("Every CommandReceiverInterface must get_next_command")
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must get_next_command")
        