package main

import (
    "flag"
    "os"
    "os/exec"
    "log"
    "io"
    "io/ioutil"
    "encoding/json"    
)

type UnlockRunnerConf struct {
    UnlockDirectory string
    PythonPathEnvVar string
    PythonPath string
    UnlockRuntime string
}
 
func ParseConf(runnerConfFile string) UnlockRunnerConf {
    log.Printf("Confile = "+runnerConfFile)
    file, e := ioutil.ReadFile(runnerConfFile)
    if e != nil {
        log.Fatalf("File error: %v\n", e)
    }
    var conf UnlockRunnerConf
    json.Unmarshal(file, &conf)
    return conf
}

func main() {
    
    logf, err := os.OpenFile(`unlock.log`, os.O_APPEND|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }    
    log.SetOutput(io.MultiWriter(logf, os.Stdout))

    var runnerConf = UnlockRunnerConf {`C:\Unlock`,
            `C:\Python33;C:\Python33\Lib;C:\Python33\Lib\site-packages;C:\Python33\Lib\site-packages\unlock;C:\Python27\DLLs`,
            `C:\Python33\python.exe`,
            `C:\Python33\Lib\site-packages\unlock\unlock_runtime.py`}
            
    var confFile = flag.String("conf", "", "path to the configuration; if not set the default is used")
    var fullscreen = flag.Bool("fullscreen", false, "make unlock fullscreen; overrides conf file settings")
    var fps = flag.Bool("fps", false, "displays the frequence per second; overrides the conf file setting")
    var signal = flag.String("signal", "", "selects the signaling system; valid values are: random, mobilab, enobio; default value is random; overrides the config file setting")
    
    flag.Parse()
    var unlock_cmd = runnerConf.PythonPath + ` ` + runnerConf.UnlockRuntime + ` `

    if *confFile != `` {
        unlock_cmd += ` -c `+*confFile    
    }
    
    if *fullscreen {
        unlock_cmd += ` -n `
    }
    
    if *fps {
        unlock_cmd += ` -f `
    }
    
    if *signal != `` {
        unlock_cmd += ` -s `+*signal
    }

    cmd, err := exec.Command("cmd", "/C", unlock_cmd).CombinedOutput()
    if len(cmd) > 0 {
        log.Printf("%s\n",cmd)
    }
    if err != nil {
        log.Fatalln(`FATAL: Unlock Runtime failed`)
    }
}
