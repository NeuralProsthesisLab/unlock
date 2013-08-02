# Created By: Karl Wiegand (wiegand@ccs.neu.edu)
# Date Created: Tue Mar  5 12:14:06 EST 2013
# Description: Main program file for FastPad, a letter-based
#   typing interface for the Unlock project

# Requirements for Unlock
from core import UnlockApplication

# Standard libraries
import sys

# Platform-specific imports
if sys.platform.startswith("linux"):
    try:
        from espeak import espeak
    except:
        raise Exception("ERROR: Missing python-espeak module!")
elif sys.platform.startswith("darwin"):
    import subprocess

class FastButton():
    """
    Class for a FastPad button.
    """

    def __init__(this, screen, rect, labels, actions):
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
        this.rect = rect
        screen.drawLine(rect[0], rect[1],
                rect[0], rect[1] + rect[3])
        screen.drawLine(rect[0], rect[1] + rect[3],
                rect[0] + rect[2], rect[1] + rect[3])
        screen.drawLine(rect[0] + rect[2], rect[1] + rect[3],
                rect[0] + rect[2], rect[1])
        screen.drawLine(rect[0] + rect[2],
                rect[1], rect[0], rect[1])

        # Draw the labels
        this.texts = []
        this.rects = []
        this.texts.append(screen.drawText(labels[0],
                rect[0] + (.5 * rect[2]), rect[1] + (.75 * rect[3])))
        this.rects.append((
            rect[0] + (.5 * rect[2]) - this.texts[-1].content_width/2,
            rect[1] + (.75 * rect[3]) - this.texts[-1].content_height * 0.35,
            this.texts[-1].content_width,
            this.texts[-1].content_height * .65))
        if len(labels) > 1:

            # Calculate the sub-label positions
            width = rect[2] / (len(labels) - 1)

            # Draw the sub-labels
            left = rect[0] + (width / 2)
            for label in labels[1:]:
                this.texts.append(screen.drawText(label,
                    left, rect[1] + (.25 * rect[3]),
                    size = int(.65 * this.texts[0].font_size)))
                this.rects.append((
                    left - this.texts[-1].content_width/2,
                    rect[1] + (.25 * rect[3]) - this.texts[-1].content_height * 0.35,
                    this.texts[-1].content_width,
                    this.texts[-1].content_height * 0.65))
                left += width

        # Store the labels and actions
        this.labels = labels
        this.actions = actions
        while len(this.actions) < len(this.labels):

            # Expand function pointers, if necessary
            this.actions.append(this.actions[-1])

        # Initialize links to other buttons
        this.up = None
        this.down = None
        this.left = None
        this.right = None

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

    def __init__(this, screen):
        """
        Initialize internal data structures.

        Input:
            screen -- (Unlock Screen) Drawing area

        Raises an Exception if anything goes wrong.
        """
        # Call our parent's constructor
        super(FastPad, this).__init__(screen)

        # Get the GUI calculations
        this.screen = screen
        textH = .2 * screen.height
        padW = .5 * screen.width
        padH = screen.height - textH
        padL = (screen.width - padW) / 2
        buttonW = padW / 3
        buttonH = (screen.height - textH) / 4

        # Create the text bar
        this.textRect = screen.drawRect(0, padH, screen.width, textH)
        this.text = screen.drawText("",
                screen.width / 2, screen.height - (textH / 2))
        this.text.width = screen.width
        
        # Create the buttons
        this.buttonB = FastButton(
                this.screen,
                (padL, 0, buttonW, buttonH),
                ["<"],
                [this.removeText],
                )
        this.button0 = FastButton(
                this.screen,
                (padL + buttonW, 0, buttonW, buttonH),
                ["0", "_"],
                [this.addText],
                )
        this.buttonE = FastButton(
                this.screen,
                (padL + (2 * buttonW), 0, buttonW, buttonH),
                [">"],
                [this.speakText],
                )
        this.button7 = FastButton(
                this.screen,
                (padL, buttonH, buttonW, buttonH),
                ["7", "P", "Q", "R", "S"],
                [this.addText],
                )
        this.button8 = FastButton(
                this.screen,
                (padL + buttonW, buttonH, buttonW, buttonH),
                ["8", "T", "U", "V"],
                [this.addText],
                )
        this.button9 = FastButton(
                this.screen,
                (padL + (2 * buttonW), buttonH, buttonW, buttonH),
                ["9", "W", "X", "Y", "Z"],
                [this.addText],
                )
        this.button4 = FastButton(
                this.screen,
                (padL, buttonH * 2, buttonW, buttonH),
                ["4", "G", "H", "I"],
                [this.addText],
                )
        this.button5 = FastButton(
                this.screen,
                (padL + buttonW, buttonH * 2, buttonW, buttonH),
                ["5", "J", "K", "L"],
                [this.addText],
                )
        this.button6 = FastButton(
                this.screen,
                (padL + (2 * buttonW), buttonH * 2, buttonW, buttonH),
                ["6", "M", "N", "O"],
                [this.addText],
                )
        this.button1 = FastButton(
                this.screen,
                (padL, buttonH * 3, buttonW, buttonH),
                ["1"],
                [this.addText],
                )
        this.button2 = FastButton(
                this.screen,
                (padL + buttonW, buttonH * 3, buttonW, buttonH),
                ["2", "A", "B", "C"],
                [this.addText],
                )
        this.button3 = FastButton(
                this.screen,
                (padL + (2 * buttonW), buttonH * 3, buttonW, buttonH),
                ["3", "D", "E", "F"],
                [this.addText],
                )

        # Link the buttons to each other
        this.button1.up = this.buttonB
        this.button1.down = this.button4
        this.button1.left = this.button3
        this.button1.right = this.button2
        this.button2.up = this.button0
        this.button2.down = this.button5
        this.button2.left = this.button1
        this.button2.right = this.button3
        this.button3.up = this.buttonE
        this.button3.down = this.button6
        this.button3.left = this.button2
        this.button3.right = this.button1
        this.button4.up = this.button1
        this.button4.down = this.button7
        this.button4.left = this.button6
        this.button4.right = this.button5
        this.button5.up = this.button2
        this.button5.down = this.button8
        this.button5.left = this.button4
        this.button5.right = this.button6
        this.button6.up = this.button3
        this.button6.down = this.button9
        this.button6.left = this.button5
        this.button6.right = this.button4
        this.button7.up = this.button4
        this.button7.down = this.buttonB
        this.button7.left = this.button9
        this.button7.right = this.button8
        this.button8.up = this.button5
        this.button8.down = this.button0
        this.button8.left = this.button7
        this.button8.right = this.button9
        this.button9.up = this.button6
        this.button9.down = this.buttonE
        this.button9.left = this.button8
        this.button9.right = this.button7
        this.buttonB.up = this.button7
        this.buttonB.down = this.button1
        this.buttonB.left = this.buttonE
        this.buttonB.right = this.button0
        this.button0.up = this.button8
        this.button0.down = this.button2
        this.button0.left = this.buttonB
        this.button0.right = this.buttonE
        this.buttonE.up = this.button9
        this.buttonE.down = this.button3
        this.buttonE.left = this.button0
        this.buttonE.right = this.buttonB

        # Initialize the state
        this.mode = "CURSOR"
        this.currButton = this.button5
        this.currIndex = 0
        this.selTime = 0
        this.setMode(this.mode, this.currButton)

    def addText(this, label):
        """
        Add the given label to the current text if
        there is enough space.

        Input:
            label -- (str) The text to add

        Raises an Exception if anything goes wrong.
        """
        prev = this.text.text
        this.text.text += label
        if this.text.content_width > this.text.width:
            this.text.text = prev

    def removeText(this, label):
        """
        Removes 1 character from the end of the current
        text, if available.
        
        Input:
            label -- (str) Unused

        Raises an Exception if anything goes wrong.
        """
        if len(this.text.text) >= 1:
            this.text.text = this.text.text[:-1]

    def speakText(this, label):
        """
        Speaks the current text out via a TTS if we're
        on a supported platform.

        Input:
            label -- (str) Unused

        Raises an Exception if anything goes wrong.
        """
        text = this.text.text.replace("_", " ")
        if sys.platform.startswith("linux"):
            espeak.synth(text)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["say", text])

        this.text.text = ""

    def setMode(this, mode, button):
        """
        Set the FastPad into the given state/mode.

        Input:
            mode -- (str) One of "CURSOR" or "SELECT"
            button -- (FastButton) Where is the cursor
                or selection marker?

        Raises an Exception if anything goes wrong.
        """
        # Clear the old rectangle
        this.screen.drawRect(
                this.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                this.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                this.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                this.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                color = FastPad.BG_COLOR,
                fill = True,
                )

        # We're currently in CURSOR mode
        if this.mode == "CURSOR":

            # And remaining in CURSOR mode
            if mode == "CURSOR":

                # Set the new location
                this.currButton = button

                # Draw the new rectangle
                this.screen.drawRect(
                        this.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                        this.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                        this.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                        this.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

            # And switching to SELECT mode
            elif mode == "SELECT":

                # Draw the new rectangle
                this.screen.drawRect(
                        this.currButton.rects[this.currIndex][0],
                        this.currButton.rects[this.currIndex][1],
                        this.currButton.rects[this.currIndex][2],
                        this.currButton.rects[this.currIndex][3],
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

        # We're currently in SELECT mode
        elif this.mode == "SELECT":

            # And remaining in SELECT mode
            if mode == "SELECT":

                # Rotate the index
                this.currIndex += 1
                if this.currIndex >= len(this.currButton.rects):
                    this.currIndex = 0

                # Draw the new rectangle
                this.screen.drawRect(
                        this.currButton.rects[this.currIndex][0],
                        this.currButton.rects[this.currIndex][1],
                        this.currButton.rects[this.currIndex][2],
                        this.currButton.rects[this.currIndex][3],
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

            # And switching to CURSOR mode
            elif mode == "CURSOR":

                # Call the selected item's action
                this.currButton.actions[this.currIndex](
                        this.currButton.labels[this.currIndex])

                # Reset the index
                this.currIndex = 0

                # Set the new location
                this.currButton = button

                # Draw the new rectangle
                this.screen.drawRect(
                        this.currButton.rect[0] + FastPad.CURSOR_MARGIN,
                        this.currButton.rect[1] + FastPad.CURSOR_MARGIN,
                        this.currButton.rect[2] - (2 * FastPad.CURSOR_MARGIN),
                        this.currButton.rect[3] - (2 * FastPad.CURSOR_MARGIN),
                        color = FastPad.CURSOR_COLOR,
                        fill = True,
                        )

        # Set the new mode
        this.mode = mode

    def update(this, timeDelta, decision, selection):
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

            this.setMode("CURSOR", this.currButton.left)

        elif decision == FastPad.RIGHT:

            this.setMode("CURSOR", this.currButton.right)

        elif decision == FastPad.UP:

            this.setMode("CURSOR", this.currButton.up)

        elif decision == FastPad.DOWN:

            this.setMode("CURSOR", this.currButton.down)

        elif selection:

            this.setMode("SELECT", this.currButton)

            # We've changed our selection, so reset the timer
            this.selTime = 0

        else:

            # If we're in selection mode, track the time
            if this.mode == "SELECT":

                # Add the time
                this.selTime += timeDelta

                # Should we select this item?
                if this.selTime >= FastPad.SELECT_TIME:

                    this.selTime = 0
                    this.setMode("CURSOR", this.currButton)

            # If we're not in selection mode, reset the timer
            else:
                this.selTime = 0
