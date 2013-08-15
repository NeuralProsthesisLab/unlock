#ifndef PORTABILITY_HPP
#define PORTABILITY_HPP
#ifdef MSVC && DLL_LINK
#define DllExport __declspec(dllexport)
#else
#define DllExport
#endif
#endif