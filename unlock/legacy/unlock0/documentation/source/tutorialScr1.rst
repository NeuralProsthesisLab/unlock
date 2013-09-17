screen.py Tutorial Part 1: Properties and Lines
=================

We have gone through the steps for a basic BCI app, and how to properly call it and run it.
All of our apps are GUI based. There is some graphical element to what is being used whether it is
an internet browser, or a e-mail client. There are many graphics libraries available for Python,
however the one we have chose is Pyglet. Pyglet is a wonderful low-level, Open.GL based graphics library, that
allows for hardware optimization. Its only fault is that Pyglet's syntax can be time consuming to learn and use.
Therefore we have created this class Screen in order to use Pyglet's function but in an intuitive way.

For developers that would rather use the API documentation to learn more about screen.py, can go straight to the core.screen module

Screen gives you five main methods for drawing objects to the screen. These are drawText, drawLine, drawLinePlot,
drawRect, and loadSprite. There are also four methods that return properties of the screen. These are get_offset, get_size,
get_width, and get_height. There is a final method called addGroup which will be explained last.

Lines
-----------------

So the easiest thing to draw to the screen is a line.
A line is just the shortest distance between two points.
So in order to have a line we need to start with two points.
Let's look at some example code below.

>>> from core import UnlockApplication
...
... class Line1(UnlockApplication):
... name = "line_1"
...
... def __init__(self, screen):
...
...     super(self.__class__, self).__init__(screen)
...
...     w       = screen.get_width()
...     h       = screen.get_height()
...
...     half_w  = w/2
...     half_h  = h/2
...
...     self.line1  = screen.drawLine(0, half_h, w, half_h)
...
... def update(self, dt, decision, selection):
...     """Updates with every new decision or selection"""
...     pass

This should look very much like the app code we had for HelloWorld with a few things changed.
First of all the class name is changed, as well as the class member: "name".
I have also defined some parameters from the screen that I want to use.

>>> w       = screen.get_width()
... h       = screen.get_height()
...
... half_w  = w/2
... half_h  = h/2

screen.get_width and screen.get_height do exactly what they say.
They return the width and height respectively of the screen being used.
screen.get_size is similar that it returns both the width and height as a list.

I also defined half of the screen vertically and horizontally so I can use those values as well.
I will refer to the horizontal plane as the x-direction, and the vertical direction as the y-direction.
The origin will be in the lower left hand corner of the screen.
For this script, all I am interested is one line drawn across the center of the screen horizontally.
That means my first point will have x-coordinate of 0 and a y-coordinate of half of the screen height.
My second point will have x-coordinate of the full screen width, and y-coordinate again at half of the screen height.
The function to draw this line will be screen.drawLine(x1, y1, x2, y2), and will be called like this.

>>>
...     self.line1  = screen.drawLine(0, half_h, w, half_h)

I put in the values of my first point which are (0, half_h) and then the values of my second point (w,half_h)

Now if we want to see what this looks like, we need to make sure to set up the other two parts of running apps.
The first is to add it out runtime script like so:

>>> from core import Line1
... from apps import HelloWorld
...
... def get_apps(window):
...
...     full = Screen(0,0,window.width, window.height)
...
...     app1 = Line1(full)
...
...     return [app1]
...
... if __name__ == '__main__':
...     from core import viewport
...     viewport.controller.apps = get_apps(viewport.window)
...     viewport.start()

As well as adding the correct __init__.py files in the app folder and subfolders.
This app on the screen will look something like this.

.. figure:: images/H_line.png
   :align: center

So now we have the most basic shape on the drawn on the screen!

The default color of lines are white, but we can make it whichever color we want.
For example if we want the line to be red, we can set the parameter in the function

>>>
...     red =(255,0,0)
...     self.line1  = screen.drawLine(0, half_h, w, half_h, color=red)

and it will show up like this:

.. figure:: images/H_line2.png
   :align: center

.. note:: The value for line color is a tuple of length = 3

Now, let's move on to rectangles and text.
