screen.py Tutorial Part 2: Rectangles and Decisions
==================

Rectangles
---------------

Rectangles are very similar to lines in that it requires a set of points, and some very basic variables
The function to use to draw a rectangle is screen.drawRect(x,y,width,height).
X is the x-coordinate of the leftmost coordinate of the rectangle, and
Y is the y-coordinate of the bottommost coordinate of the rectangle.
Width is the width of the rectangle, and height is the height.
These are not necessarily the points of the topmost and rightmost coordinates, but
instead the number of pixels away from the rectangles (x,y) origin.
Let's take a look at what an app with rectangles looks like.

>>> from core import UnlockApplication
...
... class Rectangle1(UnlockApplication):
... name = "rectangle_1"
...
...    def __init__(self, screen):
...
...        super(self.__class__, self).__init__(screen)
...        w       = screen.get_width()
...        h       = screen.get_height()
...
...        half_w  = w/2
...        half_h  = h/2
...
...        green   = (0,255,0)
...
...        self.rect1  = screen.drawRect(0,0, half_w, half_h, color=green)
...
...    def update(self, dt, decision, selection):
...        """Updates with every new decision or selection"""
...        pass

As you can see we are trying to draw one rectangle, with an origin at (0,0).
It will have width and height of the half the screen width and half the screen height.

This is what it looks like however, when it is called in the runtime script.

.. figure:: images/rectangle1.png
   :align: center

We can't see the bottom or left parts of the rectangle.
Its helpful, when drawing shapes to the screen, to be aware of little things like this,
when we can't see all of the parts of the screen.

We can do two things to fix this. The first is to not draw shapes so close to the edge of the screen.
The second is to draw in a buffer.
In the second version of the code, I have placed the green rectangle in the center of the screen,

The code looks like this now.

>>> from core import UnlockApplication
...
... class Rectangle2(UnlockApplication):
... name = "rectangle_2"
...
...    def __init__(self, screen):
...
...        super(self.__class__, self).__init__(screen)
...        w       = screen.get_width()
...        h       = screen.get_height()
...
...        buffer  = {'g':0.25}
...        originG = [w*buffer['g'],h*buffer['g']]
...        sizeG   = [w*(1-2*buffer['g']),h*(1-2*buffer['g'])]
...
...        green   = (0,255,0)
...
...        self.rect1  = screen.drawRect(originG[0],originG[1], sizeG[0], sizeG[1], color=green)
...
...    def update(self, dt, decision, selection):
...        """Updates with every new decision or selection"""
...        pass

And appears like this:

.. figure:: images/rectangle2.png
   :align: center

In the Rectangle2 class you will notice that i have set three new variables.
buffer is a dictionary that associates 'g' with 0.25.
originG sets my origin for the rectangle.
In this case I want the x-coordinate of the rectangle to be at 25% of the total width,
and the y-coordinate of the rectangle to be at 25% of the total height.
sizeG sets the total size of the rectangle. This is trickier
I start with the total width and height of the screen times 1.
From this I want to subtract 25% of the screen on both sides.
So I do 2*my buffer percentage subtracted by 1 to give me the amount of screen I want in each direction.

There is one more trick I want to share with you about rectangles. That is moving them around the screen.
In the next example code, class Rectangle3, I take the rectangle from before and I add a new method.
This method is moveRect(box, x_step, y_step)

>>> from core import UnlockApplication
...
... class Rectangle3(UnlockApplication):
... name = "rectangle_3"
...
...    def __init__(self, screen):
...
...        super(self.__class__, self).__init__(screen)
...        w       = screen.get_width()
...        h       = screen.get_height()
...
...        buffer  = {'g':0.25}
...        originG = [w*buffer['g'],h*buffer['g']]
...        sizeG   = [w*(1-2*buffer['g']),h*(1-2*buffer['g'])]
...
...        green   = (0,255,0)
...
...        self.rect1  = screen.drawRect(originG[0],originG[1], sizeG[0], sizeG[1], color=green)
...
...    def update(self, dt, decision, selection):
...        """Updates with every new decision or selection"""
...        if decision:
...            if decision == 1:
...                self.moveBox(self.rect1,0,1)
...            elif decision == 2:
...                self.moveBox(self.rect1,0,-1)
...            elif decision == 3:
...                self.moveBox(self.rect1,-1,0)
...            elif decision == 4:
...                self.moveBox(self.rect1,1,0)
...
...    def moveBox(self, box, x_step, y_step):
...        """Moves box by n x_step or y_step. """
...        if x_step:
...            box.vertices[::2] = [i + int(x_step)*self.x_pix for i in box.vertices[::2]]
...        if y_step:
...            box.vertices[1::2] = [i + int(y_step)*self.y_pix for i in box.vertices[1::2]]

I define how many pixels I want every x movement and y movement to be in the __init__ method.
I then add code to the update method with a decision.
Decisions are either a 1,2,3 or 4 representing up, down, left and right.
As you can see I have set the update function to add or subtract a step from the rectangle vertices
depending on what decision it receives.
For BCI, the decision is something a user will make with the EEG system.
For testing purposes, you can use the arrow keys.
Try out class Rectangle3.

Now that we have mastered Rectangles we can move on to Text and Sprites.

