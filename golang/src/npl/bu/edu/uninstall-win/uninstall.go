package main

import (
    "os"
    "log"
    "path/filepath"
    "npl/bu/edu/conf"
)

func main() {
    conf := unlockconf.ParseConf(`conf.json`)

    if err := os.RemoveAll(filepath.Join(conf.PythonBasePath, `Lib\site-packages\unlock`)); err != nil {
        log.Fatalln(err)
    }
    
    if err := os.Remove(filepath.Join(conf.PythonBasePath, `Lib\site-packages\unlock-0.3.7-py3.3.egg-info`)); err != nil {
        log.Fatalln(err)
    }
}