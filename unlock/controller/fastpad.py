# Created By: Karl Wiegand (wiegand@ccs.neu.edu)
# Date Created: Tue Mar  5 12:14:06 EST 2013
# Description: Main program file for FastPad, a letter-based
#   typing interface for the Unlock project

# Requirements for Unlock
from core import UnlockApplication

# Standard libraries
import sys

# Platform-specific imports
#if sys.platform.startswith("linux"):
#    try:
#        from espeak import espeak
#    except:
#        raise Exception("ERROR: Missing python-espeak module!")
#elif sys.platform.startswith("darwin"):
#    import subprocess

import subprocess

class FastButton(object):
    """
    Class for a FastPad button.
    """

    def __init__(self, screen, rect, labels, actions):
        """
        Initialize the internal data structures and
        graphical button layout.

        Input:
            screen -- (Unlock Screen) Drawing area
            rect -- (tuple(int, int, int, int)) Rectangle
                with x, y, width, and height
            labels -- (list(str)) Strings to display on
                the button; first is the biggest
            actions -- (list(funcs)) Actions to perform
                when labels are selected; a function will
                be passed the label as its argument

        Raises an Exception if anything goes wrong.
        """

        # Draw the button border -- hack around Unlock's drawRect()
        #screen.drawRect(*rect) # This would be nicer...
        self.rect = rect
        screen.drawLine(rect[0], rect[1],
                rect[0], rect[1] + rect[3])
        screen.drawLine(rect[0], rect[1] + rect[3],
                rect[0] + rect[2], rect[1] + rect[3])
        screen.drawLine(rect[0] + rect[2], rect[1] + rect[3],
                rect[0] + rect[2], rect[1])
        screen.drawLine(rect[0] + rect[2],
                rect[1], rect[0], rect[1])

        # Draw the labels
        self.texts = []
        self.rects = []
        self.texts.append(screen.drawText(labels[0],
                rect[0] + (.5 * rect[2]), rect[1] + (.75 * rect[3])))
        self.rects.append((
            rect[0] + (.5 * rect[2]) - self.texts[-1].content_width/2,
            rect[1] + (.75 * rect[3]) - self.texts[-1].content_height * 0.35,
            self.texts[-1].content_width,
            self.texts[-1].content_height * .65))
        if len(labels) > 1:

            # Calculate the sub-label positions
            width = rect[2] / (len(labels) - 1)

            # Draw the sub-labels
            left = rect[0] + (width / 2)
            for label in labels[1:]:
                self.texts.append(screen.drawText(label,
                    left, rect[1] + (.25 * rect[3]),
                    size = int(.65 * self.texts[0].font_size)))
                self.rects.append((
                    left - self.texts[-1].content_width/2,
                    rect[1] + (.25 * rect[3]) - self.texts[-1].content_height * 0.35,
                    self.texts[-1].content_width,
                    self.texts[-1].content_height * 0.65))
                left += width

        # Store the labels and actions
        self.labels = labels
        self.actions = actions
        while len(self.actions) < len(self.labels):

            # Expand function pointers, if necessary
            self.actions.append(self.actions[-1])

        # Initialize links to other buttons
        self.up = None
        self.down = None
        self.left = None
        self.right = None

class FastPad(UnlockApplication):
    """
    Main class for an instance of FastPad.

    This application works like a phone number pad.  To type a character,
    move the cursor onto the appropriate button.  Select that button
    until the desired character is highlighted.  The character will be
    typed and added to the current string when: (1) the cursor is moved
    to a different button, or (2) when the timeout has been reached.  This
    mimics phone-typing functionality, so typing two of the same characters
    in a row requires waiting for the timeout or artificially moving the
    cursor away and back again.

    The left arrow ("<") is backspace, the underscore inserts a space (" "),
    and the right arrow (">") speaks out the current string by sending it
    to a TTS (Text-to-Speech) engine if FastPad is running on a supported
    platform.

    TODO: Where can we put the language prediction modules, so that we
    can experiment with T9-like prediction or cursor-hopping schemes?
    """

    # Static constants
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    BG_COLOR = (0, 0, 0) # Color of the background
    CURSOR_COLOR = (0, 0, 255) # Color of the cursor
    CURSOR_MARGIN = 2 # Margin around the cursor, in pixels
    SELECT_TIME = 2 # How many seconds before a selection activates?

    def __init__(self, screen):
        """
        Initialize internal data structures.

        Input:
            screen -- (Unlock Screen) Drawing area

        Raises an Exception if anything goes wrong.
        """
        # Call our parent's constructor
        super(FastPad, self).__init__(screen)

        # Get the GUI calculations
        self.screen = screen
        textH = .2 * screen.height
        padW = .5 * screen.width
        padH = screen.height - textH
        padL = (screen.width - padW) / 2
        buttonW = padW / 3
        buttonH = (screen.height - textH) / 4

        # Create the text bar
        self.textRect = screen.drawRect(0, padH, screen.width, textH)
        self.text = screen.drawText("",
                screen.width / 2, screen.height - (textH / 2))
        self.text.width = screen.width
        
        # Create the buttons
        self.buttonB = FastButton(
                self.screen,
                (padL, 0, buttonW, buttonH),
                ["<"],
                [self.removeText],
                )
        self.button0 = FastButton(
                self.screen,
                (padL + buttonW, 0, buttonW, buttonH),
                ["0", "_"],
                [self.addText],
                )
        self.buttonE = FastButton(
                self.screen,
                (padL + (2 * buttonW), 0, buttonW, buttonH),
                [">"],
                [self.speakText],
                )
        self.button7 = FastButton(
                self.screen,
                (padL, buttonH, buttonW, buttonH),
                ["7", "P", "Q", "R", "S"],
                [self.addText],
                )
        self.button8 = FastButton(
                self.screen,
                (padL + buttonW, buttonH, buttonW, buttonH),
                ["8", "T", "U", "V"],
                [self.addText],
                )
        self.button9 = FastButton(
                self.screen,
                (padL + (2 * buttonW), buttonH, buttonW, buttonH),
                ["9", "W", "X", "Y", "Z"],
                [self.addText],
                )
        self.button4 = FastButton(
                self.screen,
                (padL, buttonH * 2, buttonW, buttonH),
                ["4", "G", "H", "I"],
                [self.addText],
                )
        self.button5 = FastButton(
                self.screen,
                (padL + buttonW, buttonH * 2, buttonW, buttonH),
                ["5", "J", "K", "L"],
                [self.addText],
                )
        self.button6 = FastButton(
                self.screen,
                (padL + (2 * buttonW), buttonH * 2, buttonW, buttonH),
                ["6", "M", "N", "O"],
                [self.addText],
                )
        self.button1 = FastButton(
                self.screen,
                (padL, buttonH * 3, buttonW, buttonH),
                ["1"],
                [self.addText],
                )
        self.button2 = FastButton(
                self.screen,
                (padL + buttonW, buttonH * 3, buttonW, buttonH),
                ["2", "A", "B", "C"],
                [self.addText],
                )
        self.button3 = FastButton(
                self.screen,
                (padL + (2 * buttonW), buttonH * 3, buttonW, buttonH),
                ["3", "D", "E", "F"],
                [self.addText],
                )

        # Link the buttons to each other
        self.button1.up = self.buttonB
        self.button1.down = self.button4
        self.button1.left = self.button3
        self.button1.right = self.button2
        self.button2.up = self.button0
        self.button2.down = self.button5
        self.button2.left = self.button1
        self.button2.right = self.button3
        self.button3.up = self.buttonE
        self.button3.down = self.button6
        self.button3.left = self.button2
        self.button3.right = self.button1
        self.button4.up = self.button1
        self.button4.down = self.button7
        self.button4.left = self.button6
        self.button4.right = self.button5
        self.button5.up = self.button2
        self.button5.down = self.button8
        self.button5.left = self.button4
        self.button5.right = self.button6
        self.button6.up = self.button3
        self.button6.down = self.button9
        self.button6.left = self.button5
        self.button6.right = self.button4
        self.button7.up = self.button4
        self.button7.down = self.buttonB
        self.button7.left = self.button9
        self.button7.right = self.button8
        self.button8.up = self.button5
        self.button8.down = self.button0
        self.button8.left = self.button7
        self.button8.right = self.button9
        self.button9.up = self.button6
        self.button9.down = self.buttonE
        self.button9.left = self.button8
        self.button9.right = self.button7
        self.buttonB.up = self.button7
        self.buttonB.down = self.button1
        self.buttonB.left = self.buttonE
        self.buttonB.right = self.button0
        self.button0.up = self.button8
        self.button0.down = self.button2
        self.button0.left = self.buttonB
        self.button0.right = self.buttonE
        self.buttonE.up = self.button9
        self.buttonE.down = self.button3
        self.buttonE.left = self.button0
        self.buttonE.right = self.buttonB

        # Initialize the state
        self.mode = "CURSOR"
        self.currButton = self.button5
        self.currIndex = 0
        self.selTime = 0
        self.setMode(self.mode, self.currButton)

    def addText(self, label):
        """
        Add the given label to the current text if
        there is enough space.

        Input:
            label -- (str) The text to add

        Raises an Exception if anything goes wrong.
        """
        prev = self.text.text
        self.text.text += label
        if self.text.content_width > self.text.width:
            self.text.text = prev

    def removeText(self, label):
        """
        Removes 1 character from the end of the current
        text, if available.
        
        Input:
            label -- (str) Unused

        Raises an Exception if anything goes wrong.
        """
        if len(self.text.text) >= 1:
            self.text.text = self.text.text[:-1]

    def speakText(self, label):
        """
        Speaks the current text out via a TTS if we're
        on a supported platform.

        Input:
            label -- (str) Unused

        Raises an Exception if anything goes wrong.
        """
        text = self.text.text.replace("_", " ")
        if sys.platform.startswith("linux"):
            espeak.synth(text)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["say", text])

        self.text.text = ""

    def setMode(self, mode, button):
        """
        Set the FastPad into the given state/mode.

        Input:
            mode -- (str) One of "CURSOR" or "SELECT"
            button -- (FastButton) Where is the cursor
                or selection marker?

        Raises an Exception if anything goes wrong.
        """
        # Clear the old rectangle
        self.screen.drawRect(
                self.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                self.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                self.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                self.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                color = FastPad.BG_COLOR,
                fill = True,
                )

        # We're currently in CURSOR mode
        if self.mode == "CURSOR":

            # And remaining in CURSOR mode
            if mode == "CURSOR":

                # Set the new location
                self.currButton = button

                # Draw the new rectangle
                self.screen.drawRect(
                        self.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                        self.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                        self.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                        self.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

            # And switching to SELECT mode
            elif mode == "SELECT":

                # Draw the new rectangle
                self.screen.drawRect(
                        self.currButton.rects[self.currIndex][0],
                        self.currButton.rects[self.currIndex][1],
                        self.currButton.rects[self.currIndex][2],
                        self.currButton.rects[self.currIndex][3],
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

        # We're currently in SELECT mode
        elif self.mode == "SELECT":

            # And remaining in SELECT mode
            if mode == "SELECT":

                # Rotate the index
                self.currIndex += 1
                if self.currIndex >= len(self.currButton.rects):
                    self.currIndex = 0

                # Draw the new rectangle
                self.screen.drawRect(
                        self.currButton.rects[self.currIndex][0],
                        self.currButton.rects[self.currIndex][1],
                        self.currButton.rects[self.currIndex][2],
                        self.currButton.rects[self.currIndex][3],
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

            # And switching to CURSOR mode
            elif mode == "CURSOR":

                # Call the selected item's action
                self.currButton.actions[self.currIndex](
                        self.currButton.labels[self.currIndex])

                # Reset the index
                self.currIndex = 0

                # Set the new location
                self.currButton = button

                # Draw the new rectangle
                self.screen.drawRect(
                        self.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                        self.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                        self.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                        self.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

        # Set the new mode
        self.mode = mode

    def update(self, timeDelta, decision, selection):
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
        if decision == FastPad.LEFT:

            self.setMode("CURSOR", self.currButton.left)

        elif decision == FastPad.RIGHT:

            self.setMode("CURSOR", self.currButton.right)

        elif decision == FastPad.UP:

            self.setMode("CURSOR", self.currButton.up)

        elif decision == FastPad.DOWN:

            self.setMode("CURSOR", self.currButton.down)

        elif selection:

            self.setMode("SELECT", self.currButton)

            # We've changed our selection, so reset the timer
            self.selTime = 0

        else:

            # If we're in selection mode, track the time
            if self.mode == "SELECT":

                # Add the time
                self.selTime += timeDelta

                # Should we select self item?
                if self.selTime >= FastPad.SELECT_TIME:

                    self.selTime = 0
                    self.setMode("CURSOR", self.currButton)

            # If we're not in selection mode, reset the timer
            else:
                self.selTime = 0
