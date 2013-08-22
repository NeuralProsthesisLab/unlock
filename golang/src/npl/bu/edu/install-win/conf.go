package main

import (
"fmt"
"os"
"encoding/json"
"io/ioutil"
)
 
type UnlockInstallConf struct {
    Host HostConf
    Unlock UnlockConf
    Python PythonConf
}

type HostConf struct {
    BaseUrl string
}

type UnlockConf struct {
    UnlockDirectory string
}

type PythonConf struct {
    PythonDirectory string
    Python string
    EasyInstall string
    Pip string
    Virtualenv string
    EnvName string    
}
 
func ParseConf(confFile string) UnlockInstallConf {
    file, e := ioutil.ReadFile(confFile)
    if e != nil {
        fmt.Printf("File error: %v\n", e)
        os.Exit(1)
    }
    fmt.Printf("%s\n", string(file))
 
    //m := new(Dispatch)
    //var m interface{}
    var conf UnlockInstallConf
    json.Unmarshal(file, &conf)
    fmt.Printf("Results: %v\n", conf)
    return conf
}
