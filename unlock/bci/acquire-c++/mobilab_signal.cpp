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

#include "ISignal.hpp"
#include "NonblockingSignal.hpp"
#include "Portability.hpp"
#include "PythonSignal.hpp"
#include "ITimer.hpp"
#include "WinTimer.hpp"
#include "MobilabSignal.hpp"
#include "unlock_signal.hpp"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <vector>
#include <stdint.h>


// ain = 120, dio = 0, comPort = "COM5"
ISignal* create_mobilab_signal(ITimer* pTimer, int32_t ain, int32_t dio, std::string comPort) {
  MobilabSignal* pMobilabSignal = new MobilabSignal(pTimer, ain, dio, comPort);
  return pMobilabSignal;
}

PythonSignal* create_blocking_mobilab_signal(ITimer* pTimer, int32_t ain, int32_t dio, std::string comPort) {
  ISignal* pMobilabSignal = create_mobilab_signal(pTimer, ain, dio, comPort);
  PythonSignal* pPythonSignal = new PythonSignal(pMobilabSignal, pTimer);
  return pPythonSignal;
}

PythonSignal* create_nonblocking_mobilab_signal(ITimer* pTimer, int32_t ain, int32_t dio, std::string comPort) {
  ISignal* pMobilabSignal = create_mobilab_signal(pTimer, ain, dio, comPort);
  NonblockingSignal* pNonblockingSignal = new NonblockingSignal(pMobilabSignal);
  PythonSignal* pPythonSignal = new PythonSignal(pNonblockingSignal, pTimer);
  return pPythonSignal;
}

BOOST_PYTHON_MODULE(mobilab_signal)
{
  class_<std::vector<int32_t> >("int32_vector")
        .def(vector_indexing_suite<std::vector<int32_t> >() );
        
  def("create_blocking_mobilab_signal", create_blocking_mobilab_signal, return_value_policy<manage_new_object>());
  def("create_nonblocking_mobilab_signal", create_nonblocking_mobilab_signal, return_value_policy<manage_new_object>());

}

