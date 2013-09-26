
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
package main

import (
    "npl/bu/edu/unzip"
    "os"
    "os/exec"
    "log"
    "path/filepath"
    "io"
)

func cwdAbs() string {
    cwd, err := filepath.Abs("")
    if err != nil {
        log.Fatalln(err)
    }
    return cwd
}



func main() {
    logf, err := os.OpenFile("boost-win.log", os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln("Failed to create boost-win.log", err)
    }
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    
    log.Println(" Version 0.91 ")

    u := &unzip.Unzip{"boost_1_54_0.zip", "", nil}
    if err := u.Expand(); err != nil {
        log.Fatalln("Failed to expand boost_1_54_0.zip ", err)
    }

    boost_dir := cwdAbs()
    
    if err := os.Chdir("boost_1_54_0"); err != nil {
        log.Fatalln("Failed to build Boost; the directory boost_1_54_0 does not exist ", err)
    }

    build_dir := cwdAbs()
   bootstrap_cmd := "/C "+build_dir+"\\"+"bootstrap"
   log.Println("Executing: "+bootstrap_cmd)
    cmd := exec.Command("cmd", bootstrap_cmd)
    if err := cmd.Run(); err != nil {
        log.Fatalln("Failed to execute boostrap command: "+bootstrap_cmd, err)
    }
    log.Println("Success: "+bootstrap_cmd)
//.\b2 install --prefix="c:\Users\jpercent\unlock\unlock\neural\acquire-c++\boost\win-x86-msvc-10" address-model=32 --with-python --with-random --with-system --with-test --with-thread --with-chrono --with-date_time runtime-link=shared link=shared

/*
ost/boost_1_54_0/boost_1_54_0
$ cat project-config.jam
import option ;

using msvc ;

using python : 3.3 : C:\\Python33\\ ;
option.set keep-going : false ;
*/

    b2_cmd :=  "/C "+build_dir+"\\"+"b2 install --prefix="+boost_dir+"\\win-x86-msvc-10  address-model=32  runtime-link=shared link=shared"
    log.Println("Executing: "+b2_cmd)    
    cmd = exec.Command("cmd", b2_cmd)
    if err := cmd.Run(); err != nil {
        log.Fatalln("Failed to execute b2: ", err)
    }

}
