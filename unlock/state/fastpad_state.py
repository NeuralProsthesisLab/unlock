from unlock.state.state import UnlockState

class FastPadState(UnlockState):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SELECT_TIME = 2
    def __init__(self):
       # Initialize the state
        super(FastPadState, self).__init__()
        self.previous_mode = "CURSOR"
        self.mode = "CURSOR"
        self.currButton = None
        self.button = None
        self.selTime = 0
        self.noop = False
            
    def process_command(self, command):
        """
        Update the screen; called periodically on refresh.

        Input:
            timeDelta -- (float) Number of seconds since the
                previous call to update()
            decision -- (int) Decision, if any; one of UP, DOWN,
                LEFT, or RIGHT
            selection -- (int) 1 if a selection was made

        Raises an Exception if anything goes wrong.
        """
        self.noop = False
        if command.decision == FastPadState.LEFT:
            
            self.mode = "CURSOR"
            self.button = self.currButton.left
                    
        elif command.decision == FastPadState.RIGHT:
            self.mode = "CURSOR"
            self.button = self.currButton.right
            
        elif command.decision == FastPadState.UP:
            self.mode = "CURSOR"
            self.button = self.currButton.up
            
        elif command.decision == FastPadState.DOWN:
            self.mode = "CURSOR"
            self.button = self.currButton.down
            
        elif command.selection:
            self.mode = "SELECT"
            self.button = self.currButton
            # We've changed our selection, so reset the timer
            self.selTime = 0
            
        else:
            # If we're in selection mode, track the time
            if self.mode == "SELECT":
                
                # Add the time
                self.selTime += command.delta
                
                # Should we select self item?
                if self.selTime >= FastPadState.SELECT_TIME:
                    
                    self.selTime = 0
                    self.mode = "CURSOR"
                    self.button = self.currButton
                else:
                    self.noop = True
                    
            # If we're not in selection mode, reset the timer
            else:
                self.selTime = 0
                self.noop = True

                