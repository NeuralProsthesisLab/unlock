

class FastPadModel(UnlockModel):
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
        if command.decision == FastPad.LEFT:
            
            self.cursor = "CURSOR"
            self.button = self.currButton.left
            
        elif command.decision == FastPad.RIGHT:
            self.cursor = "CURSOR"
            self.button = self.currButton.right
            
        elif command.decision == FastPad.UP:
            self.cursor = "CURSOR"
            self.button = self.currButton.up
            
        elif command.decision == FastPad.DOWN:
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
                if self.selTime >= FastPad.SELECT_TIME:
                    
                    self.selTime = 0
                    self.cursor = "CURSOR"
                    self.button = self.currButton
                else:
                    self.noop = True
                    
            # If we're not in selection mode, reset the timer
            else:
                self.selTime = 0
                self.noop = True

                