
// Copyright (c) James Percent, Giang Nguyen and Unlock contributors.
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

package unlockconf

import (
    "encoding/json"
    "io/ioutil"
    "log"
)
 
type UnlockInstallConf struct {
    UnlockDirectory string
    BaseUrl string
    PythonPathEnvVar string
    PythonInstallerName string
    PythonPackageName string
    PythonBasePath string
    PythonPath string
    NumpyPackageName string
    EasyInstallPath string
    PipPath string
    VirtualenvPath string
    EnvName string
    NumpyHack string
    NumpyHack1 string
    EnvPythonPath string
    EnvPipPath string
    PygletZipName string
    PygletPackageName string
    PygletDirectory string
    Avbin string
    PyserialZipName string
    PyserialPackageName string 
    PyserialDirectory string
	UnlockZipName string
    UnlockPackageName string
    UnlockPackageDirectory string
    SconsZipName string
    SconsPackageName string 
    SconsPackageDirectory string
    Unlockexe string
	VCRedistPackageName string
	PyAudioPackageName string    
    PyWinPackageName string
    UnlockExeX86PackageName string
    UnlockExeX64PackageName string
    UnlockUninstallerPackageName string
    UnlockUninstallerBatFile string
    ScipyPackageName string
}
 
func ParseConf(confFile string) UnlockInstallConf {
    log.Printf("Confile = "+confFile)
    file, e := ioutil.ReadFile(confFile)
    if e != nil {
        log.Fatalf("File error: %v\n", e)
    }
    log.Printf("------------>%s<---------------\n", string(file))
    var conf UnlockInstallConf
    json.Unmarshal(file, &conf)
    log.Printf("---------------->%v<----------------\n", conf)
    return conf
}

func WriteConf(filePath string, conf UnlockInstallConf) {
    content, err := json.Marshal(&conf)
    if err != nil {
        log.Fatalln(err)
    }
    
    err = ioutil.WriteFile(filePath, content, 0744)
    if err != nil {
        log.Fatalln(err)
    }
}
