Tutorial: __init__.py
====================

If you have looked in the containing folders of the unlock folder you will see the file names of the apps,
but you will also see a filename that is repeated many times over.

This file is __init__.py

It serves one very important function, which is to allow the developer to organize their scripts in
containing folders for ease of use, access and storage.
The __init__.py file has the exact same purpose as the __init__ method of the class we looked at in the App tutorial.
Whatever is contained within the script of __init__ will run when it is called.
In this case, whenever a folder containing a __init__.py file is imported, the commands of that __init__.py script are run.

Lets look at an example. Here is the top portion of the runtime.py script that we made in the last tutorial

>>> from core import Screen
... from apps import HelloWorld
...

These are two of the import functions used in the script. The first is importing the Screen class from the core folder.
The second is importing the HelloWorld class from the apps folder.
What does this actually mean?
It means runtime.py is going to look at the folder it is stored in (unlock project top folder) and will look for an item named core, and an item named apps.

.. figure:: images/UnlockTopFolder.png
   :align: center

   Unlock Project Top Folder

If it finds a file named apps, it will look in the file for a class named HelloWorld.
In this case it will find the folder named apps, open it, and will look for a class named HelloWorld.

.. figure:: images/UnlockappsFolder.png
   :align: center

   Unlock Project apps Folder

When the folder is opened the __init__.py script will run. If the HelloWorld class is in there, the file will import.
However, what you will find in all of our __init__.py files are lines that look like this:

>>> from menu import Menu
... from remote import BCIRemote
... from robot import Robot
... from scope import TimeScope, SpectrumScope
... from grid import GridHierarchy
... from helloworld import HelloWorld
... from diagnostic import FreqButton

More import statements! These are the contents of the __init__.py file within the apps folder that you see at the bottom.
These import statements are now selecting new folders in which to seek the same class we were looking for before: HelloWorld.
Now, the import statement is looking in the folder helloworld of the apps folder. For ease I will start using this folder hierarchy notation: apps.helloworld.
When the helloworld folder is opened, there are two items, another __init__.py and a script named helloworld.py

.. figure:: images/UnlockhelloworldFolder.png
   :align: center

   Unlock Project apps.helloworld Folder

Again, the __init__.py will run and within this script we see:

>>> from helloworld import HelloWorld
...

This is __init__.py again saying, go find an item named helloworld, and within that item, find the class HelloWorld.
Notice the formatting of the capital letters. This will make a difference when trying to import the classes you have made.

So when building your apps, it might be most useful to store your app in a containing folder.
In those cases, you will need to create __init__.py files to allow for proper imports.
Now let's go over the Tutorial on the Screen Class and Pyglet.
