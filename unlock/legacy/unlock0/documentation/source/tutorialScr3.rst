screen.py Tutorial Part 3: Text, and Selection
==================

Text
-------------

Drawing text to the screen is a little bit easier than line or rectangles.
To draw text we will use the method screen.drawText(text, x, y).
It is a simple as that. You choose a string to be your text, and then an anchor
where you want the center of the text to be.

Implementing this in code would look something like this:

>>> from core import UnlockApplication
...
... class Text1(UnlockApplication):
...     name = "text_1"
...
...     def __init__(self, screen):
...
...         super(self.__class__, self).__init__(screen)
...         w       = screen.get_width()
...         h       = screen.get_height()
...
...        half_w  = w/2
...        half_h  = h/2
...
...        blue    = (0,0,255,255)
...
...        text = 'Hello World'
...
...        self.text1 = screen.drawText(text,half_w,half_h, color=blue)
...
...    def update(self, dt, decision, selection):
...        """Updates with every new decision or selection"""
...        pass

.. Note:: Text colors values are a tuple of length four, the last value being opacity.

This is very similar to the Hello World version we looked at in the first tutorial.
Notice though that the color value is a tuple of length four not three.
This will make it harder to use one value for color when creating your apps.
The result of this app looks like this:

.. figure:: images/HelloWorld3.png
   :align: center

One neat thing about text is that you can change the parameters of the object in the update function.
For example, here is another version of the code that changes the color of the text at every selection.

>>> from core import UnlockApplication
... from random import randint
...
... class Text2(UnlockApplication):
...     name = "text_2"
...
...     def __init__(self, screen):
...
...         super(self.__class__, self).__init__(screen)
...         w       = screen.get_width()
...         h       = screen.get_height()
...
...         half_w  = w/2
...         half_h  = h/2
...
...         blue    = (0,0,255,255)
...
...         text = 'Hello World'
...
...         self.text1 = screen.drawText(text,half_w,half_h, color=blue)
...
...     def update(self, dt, decision, selection):
...         """Updates with every new decision or selection"""
...         if selection:
...             self.text1.color = (randint(0,255), randint(0,255),
...                                randint(0,255), 255)

Try this out for yourself to see how this works. Selection is the fifth input that your app can receive, after the four directional decisions.
This is meant to be a method of choosing one item or another. If for example you have a cursor that moves over multiiple items,
the selection input can allow one or more to be chosen.

There you go. There are the three most important parts of the core.screen() module.
The apps that are currently in the repository make use of these methods, as well as a few more non-important ones.
More screen Tutorials are soon to follow.
