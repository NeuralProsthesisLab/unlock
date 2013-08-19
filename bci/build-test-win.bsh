#!/bin/bash

#/cygdrive/c/Python27/Scripts/scons.bat -c 
/cygdrive/c/Python27/Scripts/scons.bat -Q
cp  boosted_bci_win_x86.dll boost/win-x86/lib/
cp  boosted_bci_win_x86.dll boost/win-x86/lib/boosted_bci.pyd
cp bci-unit-tests.* boost/win-x86/lib
cd boost/win-x86/lib
./bci-unit-tests.exe

