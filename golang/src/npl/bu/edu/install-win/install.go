package main

import (
    "npl/bu/edu/unzip"
    "net/http"
    "fmt"
    "io/ioutil"
    "os"
    "os/exec"
    "log"
    "path/filepath"
    "io"
)

func downloadAndWriteFile(url string, fileName string) {
    resp, err := http.Get(url)
    if err != nil {
        log.Fatalln(err)
    }
    
    defer resp.Body.Close()
    body, err1 := ioutil.ReadAll(resp.Body)
    if err1 != nil {
        log.Fatalln(err)
    }
    
    if err = ioutil.WriteFile(fileName, body, 0744); err != nil {
        log.Fatalln(err)
    }
}

func getWorkingDirectoryAbsolutePath() string {
    cwd, err := filepath.Abs(``)
    log.Println(`Current working directory = `, cwd)
    if err != nil {
        log.Fatalln(err)
    }
    return cwd
}

func runCommand(command string, errorMsg string, failOnError bool) bool {
    result := true
    cwd := getWorkingDirectoryAbsolutePath()
    cmd := exec.Command(`cmd`, `/C `+cwd+"\\"+command) // note the mixing of ` and "; my editor `\` are not friends
    if err := cmd.Run(); err != nil {
        if failOnError == true {
            log.Fatalln(`FATAL: `+errorMsg+`; command = `+command, err)
        } else {
            log.Println(`Non-fatal `+errorMsg+`; command = `+command, err)
        }
        result = false
    }
    return result
}

func install(command string, packageName string, failOnError bool) {
    log.Print(`Installing `+packageName+`: `)
    result := runCommand(command, `Failed to install `+packageName, failOnError)
    if result {
        fmt.Println(`Success`)
    } else {
        fmt.Println(`Failure`)
    }
}

func chdirFailOnError(directory string, errorMsg string) {
    if err := os.Chdir(directory); err != nil {
        log.Fatalln(`install-win.chdirFailOnError: ERROR: Change directory to `+directory+` failed: `+errorMsg, err)
    }
}

func unzipExpand(fileName string) {
    u := &unzip.Unzip{fileName, ``, nil}
    if err := u.Expand(); err != nil {
        log.Fatalln(`Failed to expand `+fileName, err)
    }    
}

func installZippedPythonPackage(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    log.Println(`Downloading `+packageName+`... `)
    downloadAndWriteFile(baseUrl+fileName, fileName)
    unzipExpand(fileName)
    chdirFailOnError(packageDirectory, `Failed to install `+packageName)
    command := `/C `+pythonPath+` setup.py install`
    install(command, packageName, true)
    os.Chdir(`..`)
}

func installPython(baseUrl string, pythonInstallerName string, pythonBasePath string, pythonPackageName string) {// base_python_path string) {
    command := `msiexec /i ` + pythonInstallerName + ` TARGETDIR=`+pythonBasePath+` /qb ALLUSERS=0 `
    log.Println(`Downloading `+pythonPackageName+`...`)
    downloadAndWriteFile(baseUrl+pythonInstallerName, pythonInstallerName)        
    install(command, pythonPackageName, true)
}

func installEasyInstall(baseUrl string, pythonPath string) {
    downloadAndWriteFile(baseUrl+`distribute_setup.py`, `distribute.py`)
    install(pythonPath+` distribute_setup.py`, `easy_install`, true)    
}

func installPip(easyInstallPath string) {
    install(easyInstallPath+` pip`, `pip`, true)
}

func installVirtualenv(pipPath string) {
    install(pipPath+` install virtualenv`, `virtualenv`, true)
}

func createVirtualenv(unlockDirectory string, virtualenvPath string, envName string) {
    errorMsg := `Failed to create virtual environment`
    chdirFailOnError(unlockDirectory, errorMsg)
    command := virtualenvPath+` --distribute `+envName //python27`
    runCommand(command, errorMsg, true)
}

func installPyglet12alpha(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory)
}

func installNumPy(pipPath string) {
    install(pipPath+` numpy`, `numpy`, true)
}
/*
func installNumPy171() {
    post_fn := func() {}
    installExe(`numpy-MKL-1.7.1.win32-py2.7.exe`, `NumPy-1.7.1`, true, post_fn)
}
*/
func installPySerial26(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory);
    //`pyserial-2.6.zip`, `pyserial-2.6`, `pyserial-2.6`, post_fn)
}

func installUnlock() {
/*    
    post_processing_fn := func() {
        if err := os.MkdirAll(`C:\Unlock`, 0755); err != nil {
            log.Fatalln(`Failed to make unlock directory`, err)
        }
        if err := os.Rename(`collector.py`, `C:\Unlock\collector.py`); err != nil {
            log.Fatalln(`Failed to install unlock collector`, err)
        }

        if err := os.Rename(`collector.bat`, `C:\Unlock\collector.bat`); err != nil {
            log.Fatalln(`Failed to install unlock collector`, err)
        }

        if err := os.Rename(`pygtec.py`, `C:\Unlock\pygtec.py`); err != nil {
            log.Fatalln(`Failed to install unlock collector`, err)
        }

        if err := os.Rename(`targets.png`, `C:\Unlock\targets.png`); err != nil {
            log.Fatalln(`Failed to install unlock collector`, err)
        }
    }
    installZippedPythonPackage(`unlock.zip`, `unlock`, `unlock`, post_processing_fn)
    */
}

 
func main() {
    logf, err := os.OpenFile(`unlock-install.log`, os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }
    
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    conf := ParseConf("config.json")

    installPython(conf.BaseUrl, conf.PythonInstallerName, conf.PythonBasePath, conf.PythonPackageName)
    installEasyInstall(conf.BaseUrl, conf.PythonPath)
    installPip(conf.EasyInstallPath)
    installVirtualenv(conf.PipPath)
    createVirtualenv(conf.UnlockDirectory, conf.VirtualenvPath, conf.EnvName)
    installPyglet12alpha(conf.PythonPath, conf.BaseUrl, conf.PygletZipName, conf.PygletPackageName, conf.PygletDirectory)
    installNumPy(conf.PipPath)
    installPySerial26(conf.PythonPath, conf.BaseUrl, conf.PyserialZipName, conf.PyserialPackageName, conf.PyserialDirectory)
    installUnlock()
}
