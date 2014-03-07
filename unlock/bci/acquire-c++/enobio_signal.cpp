// Copyright (c) James Percent and Unlock contributors.
// All rights reserved.
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//    1. Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//    
//    2. Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//    3. Neither the name of Unlock nor the names of its contributors may be used
//       to endorse or promote products derived from this software without
//       specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
// ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
// ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "Enobio3G.h"
#include "ISignal.hpp"
#include "NonblockingSignal.hpp"
#include "Portability.hpp"
#include "PythonSignal.hpp"
#include "EnobioSignalHandler.hpp"
#include "EnobioDataReceiver.hpp"
#include "EnobioStatusReceiver.hpp"
#include "ITimer.hpp"
#include "WinTimer.hpp"
#include "unlock_signal.hpp"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <vector>
#include <stdint.h>

using namespace boost::python;

ISignal* create_enobio_signal(ITimer* pTimer) {
  Enobio3G* pEnobio3G = new Enobio3G();
  EnobioSignalHandler* pEnobioSignalHandler = new EnobioSignalHandler(pEnobio3G, pTimer);
  
  EnobioDataReceiver* pDataReceiver = new EnobioDataReceiver(pEnobioSignalHandler);
  pEnobioSignalHandler->setEnobioDataReceiver(pDataReceiver);
  
  EnobioStatusReceiver* pStatusReceiver = new EnobioStatusReceiver(pEnobioSignalHandler);
  pEnobioSignalHandler->setEnobioStatusReceiver(pStatusReceiver);
  return pEnobioSignalHandler;
}

PythonSignal* create_blocking_enobio_signal(ITimer* pTimer) {
  ISignal* pEnobioSignalHandler = create_enobio_signal(pTimer);
  PythonSignal* pPythonSignal = new PythonSignal(pEnobioSignalHandler, pTimer);
  return pPythonSignal;
}

PythonSignal* create_nonblocking_enobio_signal(ITimer* pTimer) {
  ISignal* pEnobioSignalHandler = create_enobio_signal(pTimer);
  NonblockingSignal* pNonblockingSignal = new NonblockingSignal(pEnobioSignalHandler);
  PythonSignal* pPythonSignal = new PythonSignal(pNonblockingSignal, pTimer);
  return pPythonSignal;
}

BOOST_PYTHON_MODULE(enobio_signal)
{
  def("create_blocking_enobio_signal", create_blocking_enobio_signal, return_value_policy<manage_new_object>());
  def("create_nonblocking_enobio_signal", create_nonblocking_enobio_signal, return_value_policy<manage_new_object>());

}

