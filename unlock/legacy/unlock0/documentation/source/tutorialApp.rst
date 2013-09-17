Tutorial: Making a BCI Application(BCI App)
====================
For now, let’s focus on how to make and run an application.
To start let’s look at the format of an application script.
Below is a script for a hello world application.

>>> from core import UnlockApplication
...
... class HelloWorld(UnlockApplication):
...     name = "Hello World"
...
...     def __init__(self, screen):
...         super(self.__class__, self).__init__(screen)
...
...         self.text = screen.drawText('Hello World!', screen.width / 2,
...                                    screen.height / 2)
...
...     def update(self, dt, decision, selection):
...         pass

The following code will display the words “Hello World” in the center
of the given screen, as shown below.

.. figure:: images/HelloWorld.png
   :align: center

   Hello World

You will also notice there is a screen refresh rate in the lower left corner.
This is included for all apps.

Let’s look at each individual part of this code.

First you need to import the UnlockApplication Module from application.py in the core folder.

>>> from core import UnlockApplication
...

This is a module that sets up the basic infrastructure of this application,
and creates some easy functions, such as starting the application,
closing it, and running the update cycle.
You will not need to know what the UnlockApplication Module does.
Just make sure that it is imported in the same manner shown,
as well as calling it as part of the class. This is shown below.

Now this is your opportunity to name the class of your application.
Maybe it will be BCIbrowser or BCIremote. For this example it is HelloWorld.

>>> from core import UnlockApplication
...
... class HelloWorld(UnlockApplication):

After writing the name of the class,
beneath it you must assign a name member to the class.
This reiterates the name of the app, and is required for the UnlockApplication module.
Below this name is place to put other class members as you will see in other applications

>>> from core import UnlockApplication
...
... class HelloWorld(UnlockApplication):
...     name = "Hello World"

Next comes the methods. There are two methods that every application script is expected to have,
the first of which is the __init__. For those of you who are not well versed in object oriented programming
this is an opportunity to pick up on two important notes about OOP.
The __init__ method is the only method that is run when an instance of a class is created.
This means that when the HelloWorld is called, the only code that will be executed is code located in
the __init__ method. All of the variables and functions of __init__ will run.
If there are other methods of the class, they can be called by the __init__ method,
but otherwise are run by being calling specifically from another piece of code.

The other important thing to learn about here is the keyword self.
In python, and other languages, the word self relates to the class where it is contains.
This allows the object (instance of the class), to be called without having the same name
as the class, while still being able to call the class' variables and methods.
You will notice that when creating global variables in the __init__ method, self is used before the
variable name. It is also included by default as a input variable to most methods.

__init__ is where the preliminary variables are set,
as well as defining the input variables. Every BCI application will want the screen variable
passed to the __init__ method, and the variable declaration
super(self.__class__, self).__init__(screen) as seen below.

>>> from core import UnlockApplication
...
... class HelloWorld(UnlockApplication):
...     name = "Hello World"
...
...     def __init__(self, screen):
...         super(self.__class__, self).__init__(screen)
...
...         self.text = screen.drawText('Hello World!', screen.width / 2,
...                                    screen.height / 2)
...

From here you can assign any other variables you would like.
For the example of Hello World, we create text using the screen module.
Screen is a basic command that we will go over in a later tutorial.

The second method that is required in the unlock application is the update method.
This requires three variables to be passed to it: dt, decision, and selection.
dt provides a time step to update in case your application needs it,
decision provides a choice that the user made, such as an up, down, left, and right.
Finally selection is a fifth choice such as choosing an item the cursor is on.
For this example we are not updating the Hello World app so we will use pass on this method.

This is what the script looks all together.

>>> from core import UnlockApplication
...
... class HelloWorld(UnlockApplication):
...     name = "Hello World"
...
...     def __init__(self, screen):
...         super(self.__class__, self).__init__(screen)
...
...         self.text = screen.drawText('Hello World!', screen.width / 2,
...                                    screen.height / 2)
...
...     def update(self, dt, decision, selection):
...         pass

At this point you can add whatever other methods you want or need for your app.

Now this class will not work on its own. It requires two more scripts to run.
The Next Tutorial on runtime.py will discuss this further.
