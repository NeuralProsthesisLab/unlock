Device Wrappers
===============
This repo contains the Python wrapper code for the EEG devices used in the
Neural Prosthesis Lab. Those devices are:

 * g.Tec MOBILab and USBamp (pygtec)
 * Emotiv EPOC (pymotiv)
 * StarLab Enobio (pynobio)
 
All Python wrapper code is currently generated using SWIG. Each vendor
provided C++ API is wrapped in a common interface class for use with SWIG and
Numpy. The vendor-specific header files and libraries are not included in this
repo.