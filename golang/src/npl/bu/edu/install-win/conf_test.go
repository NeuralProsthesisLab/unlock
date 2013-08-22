package main

import(
    `testing`
    `io/ioutil`
    `encoding/json`
)

func TestParseConf(t *testing.T) {
    baseUrl := `baseurl`
    unlockDir := `unlockdir`
    pythonDir := `pythondirectory`
    python := `python`
    easyInstall := `easyinstall`
    pip := `pip`
    virtualenv := `virtualenv`
    envName := `envname` 
    hostConf := HostConf{baseUrl}
    unlockConf := UnlockConf{unlockDir}
    pythonConf := PythonConf{pythonDir, python, easyInstall, pip, virtualenv,
                             envName}
    unlockInstallConf := UnlockInstallConf{hostConf, unlockConf, pythonConf}

    if unlockInstallConf.Host != hostConf {
        t.Errorf("UnlockInstallConf(%v) = %v",unlockInstallConf.Host, hostConf)        
    }
    
    if unlockInstallConf.Unlock != unlockConf {
        t.Errorf("UnlockInstallConf(%v) = %v",unlockInstallConf.Unlock, unlockConf)        
    }
    
    if unlockInstallConf.Python != pythonConf {
        t.Errorf("UnlockInstallConf(%v) = %v",unlockInstallConf.Python, pythonConf)        
    }

    unlockConfBinary, e := json.Marshal(unlockInstallConf)
    if e != nil {
        t.Errorf("Failed to marshal unlock conf ")
    }
     
    if e := ioutil.WriteFile(`conf_test.json`, unlockConfBinary, 0700); e != nil {
        t.Errorf("Failed to open conf_test.json for writing %v\n", e)
    }
    
    parsedConf := ParseConf(`conf_test.json`)
    if parsedConf != unlockInstallConf {
        t.Errorf("parsedConf(%v) != unlockInstallConf(%v)\n", parsedConf, unlockInstallConf)
    }
}