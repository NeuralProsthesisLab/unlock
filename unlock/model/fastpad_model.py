

class FastPadModel(UnlockModel):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SELECT_TIME = 2 # How many secon
    
    def __init__(self, button5):
       # Initialize the state
        self.previous_mode = "CURSOR"
        self.currButton = self.button5
        self.button = None
        self.selTime = 0        
            
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
            
            self.cursor = "CURSOR"
            self.button = self.currButton.left
            
        elif command.decision == FastPadModel.RIGHT:
            self.cursor = "CURSOR"
            self.button = self.currButton.right
            
        elif command.decision == FastPadModel.UP:
            self.cursor = "CURSOR"
            self.button = self.currButton.up
            
        elif command.decision == FastPadModel.DOWN:
            self.cursor = "CURSOR"
            self.button = self.currButton.down
            
        elif command.selection:
            self.cursor = "SELECT"
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
                    self.cursor = "CURSOR"
                    self.button = self.currButton
                else:
                    self.noop = True
                    
            # If we're not in selection mode, reset the timer
            else:
                self.selTime = 0
                self.noop = True

                