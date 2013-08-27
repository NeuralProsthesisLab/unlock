@echo off
setx PYTHONPATH "C:\Unlock\python27;C:\Unlock\python27\Lib\;C:\Unlock\python27\Scripts\;C:\Python27\DLLs"
c:\Unlock\python27\Scripts\python.exe c:\Unlock\python27\Lib\site-packages\unlock\unlock.py --help %*
pause