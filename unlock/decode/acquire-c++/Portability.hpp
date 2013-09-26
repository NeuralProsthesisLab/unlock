#ifndef PORTABILITY_HPP
#define PORTABILITY_HPP

#if defined(MSVC) && defined(DLL_LINK)
#define DllExport __declspec(dllexport)
#else
#define DllExport
#endif

#endif
