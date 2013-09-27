Unlock Overview
----------------

Unlock is Python-based software framework for Brain-Computer Interface (BCI) enabled application development.

Development of the Unlock framework is funded by the Unlock Project.  The goal of the Unlock Project 
is to provide BCI technology to individuals suffering from locked-in syndrome (LIS).  

LIS is characterized by complete or near-complete loss of voluntary motor function with 
intact sensation and cognition.  LIS is typically the result of brain stem stroke or late 
stage amyotrophic lateral schlerosis (ALS).  Sufferers of LIS often feel completely 
isolated from friends and family due to their inability to communicate.

Features
-----------

User Installation
------------------

Developer Installation
------------------------

Examples
----------

Clone the project, create and create a branch.  If you investigate the code under the golang directory, that is were our Go code lives.  Have you gone through the Go tutorial?  That's a good place to start if you haven't done so.

You can find it here: http://tour.golang.org/#1.  After that I would read over our Go code.  We're using go as a binary installer, as a runner and also as a build script.  Not all of the code is working.  The runner works.  What type of machine are your running?

Everything currently runs on Windows x86_64.  It would run fine on Windows x86, but we have to explicitly build it.  From a Go x86 machine.  The Go cross-compile infrastructure isn't there yet. 

Best place to start is with the installer itself.  Let me know what type of machine you're running on and we'll carve out the right first project for you.

Just click on python-3.3.2.msi, and it will take you through the installer.  Same with the numpy file.

For Pyglet, you have to extract all the files from the zip.  To do so, right click and select "Extract All".  Then open cmd.exe.  Change directory to where the source was extracted.  On my system this looks like:
$ cd C:\Users\jpercent\downloads\pyglet-1.2alpha\pyglet-1.2alpha1

Then run:

$ C:\Python33\python.exe setup.py install

Then set the PYTHONPATH variable to the directory of the github repo.  You should be able to run:
$ C:\Python33\python.exe unlock_runtime.py 