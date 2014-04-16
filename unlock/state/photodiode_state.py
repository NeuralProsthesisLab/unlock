from unlock.state.state import UnlockState

__author__ = 'Graham Voysey'


class PhotodiodeScopeState(UnlockState):
    def __init__(self):
        super(PhotodiodeScopeState, self).__init__()
        self.my_state = True

    def process_command(self, command):
        if command.selection:
            print('photodiode:process_command entered',self.my_state,command.selection)
        if self.my_state and command.selection: #command.selection: "someone has hit the spacebar"
            self.my_state = False
        elif (not self.my_state) and command.selection:
            self.my_state = True
        return self.my_state

    def get_state(self):
        return self.my_state
