package main

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
