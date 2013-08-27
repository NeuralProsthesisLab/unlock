package main

import (
    "encoding/json"
    "io/ioutil"
    "log"
)
 
type UnlockInstallConf struct {
    UnlockDirectory string
    BaseUrl string
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
}
 
func ParseConf(confFile string) UnlockInstallConf {
    file, e := ioutil.ReadFile(confFile)
    if e != nil {
        log.Fatalf("File error: %v\n", e)
    }
    log.Printf("%s\n", string(file))
 
    var conf UnlockInstallConf
    json.Unmarshal(file, &conf)
    log.Printf("Results: %v\n", conf)
    return conf
}
