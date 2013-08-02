%module pymotiv

%{
#define SWIG_FILE_WITH_INIT
#include "pymotiv.h"
%}

%include <windows.i>
%include "numpy.i"

%init %{
    import_array();
%}

%apply (int* ARGOUT_ARRAY1, int DIM1) {(int* data, int n)}

%include "pymotiv.h"


