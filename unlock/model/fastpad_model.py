from .model import UnlockModel

class FastPadModel(UnlockModel):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SELECT_TIME = 2
    def __init__(self):
       # Initialize the state
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
        if command.decision == FastPadModel.LEFT:
            
            self.mode = "CURSOR"
            self.button = self.currButton.left
                    
        elif command.decision == FastPadModel.RIGHT:
            self.mode = "CURSOR"
            self.button = self.currButton.right
            
        elif command.decision == FastPadModel.UP:
            self.mode = "CURSOR"
            self.button = self.currButton.up
            
        elif command.decision == FastPadModel.DOWN:
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
                if self.selTime >= FastPadModel.SELECT_TIME:
                    
                    self.selTime = 0
                    self.mode = "CURSOR"
                    self.button = self.currButton
                else:
                    self.noop = True
                    
            # If we're not in selection mode, reset the timer
            else:
                self.selTime = 0
                self.noop = True

                