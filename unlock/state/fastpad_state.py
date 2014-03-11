# Created By: Karl Wiegand (wiegand@ccs.neu.edu)
# Date Created: Tue Mar 11 16:29:35 EDT 2014
# Description: FastPad state and behavior

# General libs
from enum import Enum

# Unlock libs
from unlock.state.state import UnlockState

class FastPadState(UnlockState):
    """Text composition on a telephone number pad."""

    # Constants: directional commands
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    # Constants: state management
    BUTTON = 1 # Cursor is inside of a button
    PAD = 2 # Cursor is a button on the pad
    VOICE = 3 # System is speaking

    # Constants: logical form of rectangular number
    # pad as lists of case-insensitive strings
    # (Note: referenced as list indices with [0, 0]
    # referring to the upper-leftmost list)
    NUMPAD = [
            [[], ["A", "B", "C"], ["D", "E", "F"]],
            [["G", "H", "I"], ["J", "K", "L"], ["M", "N", "O"]],
            [["P", "Q", "R", "S"], ["T", "U", "V"], ["W", "X", "Y", "Z"]],
            [["<"], [" "], [".", "?", "!"]],
            ]

    # Constants: strings that have special meanings
    ERASE = {"<"} # Remove the last string entry from the current text
    SPEAK = {".", "?", "!"} # Speak the current text

    def __init__(self):
        """Initialize the state."""
        super(FastPadState, self).__init__()

        # Start in the center of the pad
        self.state = FastPadState.BUTTON
        self.button = [1, 1] # Center of NUMPAD
        self.item = None # Integer list position (int) or None
        self.text = [] # List of added strings from NUMPAD
            
    def process_command(self, command):
        """Update the screen; called periodically on refresh.

        Args:
            command: (object?) The user's BCI or keyboard command
        """
        # Cache our previous state
        oldState = self.state
        oldButton = self.button
        oldItem = self.item

        # Calculate our new state
        if command.decision == FastPadState.LEFT:

            # Make the move
            self.state = FastPadState.BUTTON
            self.button[1] -= 1
            self.item = None

            # Wrap the board
            if self.button[1] < 0:
                self.button[1] = len(NUMPAD[self.button[0]])
                    
        elif command.decision == FastPadState.RIGHT:

            # Make the move
            self.state = FastPadState.BUTTON
            self.button[1] += 1
            self.item = None

            # Wrap the board
            if self.button[1] > len(NUMPAD[self.button[0]])
                self.button[1] = 0
            
        elif command.decision == FastPadState.UP:
            
            # Make the move
            self.state = FastPadState.BUTTON
            self.button[0] -= 1
            self.item = None

            # Wrap the board
            if 
            
        elif command.decision == FastPadState.DOWN:

            pass
            
        elif command.selection:
            
            pass 
