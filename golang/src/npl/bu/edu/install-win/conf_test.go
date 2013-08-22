package main

import(
    `testing`
    `io/ioutil`
    `encoding/json`
)

func TestParseConf(t *testing.T) {
    unlockDir := `unlockdir`
    baseUrl := `baseurl`
    pythonInstallerName := `pythoninstallername`
    pythonPackageName := `pythoninstallername`
    pythonBasePath := `pythonbasepath`
    pythonPath := `pythonpythonpath`
    easyInstallPath := `easyinstallPath`
    pipPath := `pipPath`
    virtualenvPath := `virtualenvPath`
    envName := `envname` 
    unlockInstallConf := UnlockInstallConf{unlockDir, baseUrl, pythonInstallerName, pythonPackageName,
                    pythonBasePath, pythonPath, easyInstallPath, pipPath, virtualenvPath,
                             envName, ``, ``, ``, ``, ``,``,``,``,`pyserail-2.6`}

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