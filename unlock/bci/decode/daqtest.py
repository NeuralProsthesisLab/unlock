__author__ = 'Graham Voysey'
from PyDAQmx import *
import numpy
import matplotlib.pyplot as pyplt

analog_input = Task()
read = int32()
data = numpy.zeros((1000,), dtype=numpy.float64)

# DAQmx Configure Code
analog_input.CreateAIVoltageChan(b'Dev1/ai0',b"",DAQmx_Val_Cfg_Default,-5.0,5.0,DAQmx_Val_Volts,None)
analog_input.CfgSampClkTiming(b"",10000.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,1000)

# DAQmx Start Code
analog_input.StartTask()

# DAQmx Read Code
analog_input.ReadAnalogF64(1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)

print("Acquired {0} points".format(read.value))

pyplt.plot(data)
pyplt.show()

