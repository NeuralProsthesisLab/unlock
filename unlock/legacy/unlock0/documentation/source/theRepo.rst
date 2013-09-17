The Unlock Repository
=============================

So now that you have downloaded Python, downloaded Git, and downloaded our Repository,
what are you looking at?

The repository that we have given to you is specifically for working with the application Graphical user interface(GUI)
Our hope is that it you will be able to use it to make your BCI based applications,
or to carry out your own experiments to aid people with LIS, and other motor disabilities.

The next few page will give tutorials on how to use our existing interface, and build your own applications
For now let's just take a quick look at the organization of the unlock repository.

This is the top folder. It has four folders named apps, core, resource, and stimulus.
It also has two scripts in the top folder which are runtime.py and runDiagnostic.py.

.. figure:: images/UnlockTopFolder.png
   :align: center
   :alt: The top-level folder

The apps folder is where we store the application modules.

.. figure:: images/UnlockappsFolder.png
   :align: center
   :alt: The apps folder

The core folder is where we store modules for the under-laying frame of the app GUI.

.. figure:: images/UnlockcoreFolder.png
   :align: center
   :alt: The core folder

The resource folder stores relevant image and text files that are used by the apps.

.. figure:: images/UnlockresourceFolder.png
   :align: center
   :alt: The resource folder

Finally, the stimuli folder holds the module for creating the SSVEP stimuli.

.. figure:: images/UnlockstimFolder.png
   :align: center
   :alt: The stimulus folder

Runtime.py is the only application that you will need run to at any given time.
If you have an experiment or demo that uses a specific set up of stimuli and applications,
you could use a version of the runtime script for that specific purpose.
runDiagnostic.py is one example of this.
runDiagnostic.py is a version of runtime.py that is et up to check for a couple of things.
It has a square stimulus in the bottom left corner, and the freqButton app running in the top left.
This allows the speed of the stimulus to be sped up or slowed down.
On the right there is a timescope and a frequency scope.
These make sure that the EEG cap is recording data from the user,
checks that the decoder is decoding data accurately,
and can give a measure of how an user reacts to a given stimulus on the left hand side.

So now that you have had a tour of the repository. You can begin with the tutorial on how to use it.

If instead you would like to go straight to the Unlock API. Click on modules in the upper or lower right.
