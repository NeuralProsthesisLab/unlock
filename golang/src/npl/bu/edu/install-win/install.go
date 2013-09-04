package main

import (
    "npl/bu/edu/unzip"
    "net/http"
    "fmt"
    "io/ioutil"
    "flag"
    "os"
    "os/exec"
    "log"
    "path/filepath"
    "io"
)

func runCommand(command string, errorMsg string, failOnError bool) bool {
    result := true
    cmd := exec.Command("cmd", "/C", command) // note the mixing of ` and "; my editor `\` are not friends
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
    log.Println("command = "+ command)
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

func downloadAndWriteFile(url string, fileName string) {
    log.Println("Downloading file "+fileName+" from URL = "+url)
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

func installZippedPythonPackage(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    log.Println(`Downloading `+packageName+`... `)
    downloadAndWriteFile(baseUrl+fileName, fileName)
    unzipExpand(fileName)
    chdirFailOnError(packageDirectory, `Failed to install `+packageName)
    log.Println("CWD = "+getWorkingDirectoryAbsolutePath())
    command := pythonPath+` setup.py install`
    install(command, packageName, true)
    os.Chdir(`..`)
}

func installPython(baseUrl string, pythonPathEnvVar string, pythonInstallerName string, pythonBasePath string, pythonPackageName string) {
    cwd := getWorkingDirectoryAbsolutePath()
    log.Println(`Downloading `+pythonPackageName+`...`)
    downloadAndWriteFile(baseUrl+pythonInstallerName, pythonInstallerName)
    log.Println(`Installing `+pythonPackageName)
    cmd := exec.Command("cmd", "/C", "msiexec /i ", cwd+"\\"+pythonInstallerName,`TARGETDIR=`+pythonBasePath,`/qb`, `ALLUSERS=0`)
    if err := cmd.Run(); err != nil {
        log.Fatalln(`FATAL: failed to install python `, err)
    }
    if err := os.Setenv(`PYTHONPATH`, pythonPathEnvVar); err != nil {
        log.Println(`Could not properly set the PYTHONPATH env variable; on some systems this can cause problems during virtual env creation`)
    }
    log.Println(`PYTHON PATH = `+os.Getenv(`PYTHONPATH`))
}

func installEasyInstall(baseUrl string, pythonPath string) {
    downloadAndWriteFile(baseUrl+`distribute_setup-py`, `distribute_setup.py`)
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
    var cwd = getWorkingDirectoryAbsolutePath()
    chdirFailOnError(unlockDirectory, errorMsg)
    command := virtualenvPath+` --system-site-packages `+envName //python27`
    runCommand(command, errorMsg, true)    
    os.Chdir(cwd)
}

func installPyglet12alpha(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory)
}

func installNumPy(baseUrl string, numpyPath string) {
    downloadAndWriteFile(baseUrl+numpyPath, numpyPath)//numpy-MKL-1.7.1.win32-py2.7.exe)
    var cwd = getWorkingDirectoryAbsolutePath()
    install(cwd+"\\"+numpyPath, `numpy`, true)
}

func installPySerial26(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory);
}

func installAvbin(baseUrl string, avbin string) {
    downloadAndWriteFile(baseUrl+avbin, avbin)
    var cwd = getWorkingDirectoryAbsolutePath()
    install(cwd+"\\"+avbin, `avbin`, true)
    // XXX - last minute hack
    data, err1 := ioutil.ReadFile(`C:\Windows\System32\avbin.dll`)
    if err1 != nil {
        log.Fatalln(err1)
    }
    
    if err := ioutil.WriteFile(`C:\Windows\SysWOW64\avbin.dll`, data, 0744); err != nil {
        log.Fatalln(err)
    }    
    
}

func installScons(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory);
}

func installUnlock(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
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
*/    
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory)
}

//var species = flag.String("species", "gopher", "the species we are studying")

// Example 2: Two flags sharing a variable, so we can have a shorthand.
// The order of initialization is undefined, so make sure both use the
// same default value. They must be set up with an init function.
var confFile = flag.String("conf", "", "Qualified file name of Unlock installation configuration file")

func createConf() UnlockInstallConf {
    if *confFile == `` {
        return UnlockInstallConf {`C:\Unlock`, `http://jpercent.org/unlock/`, `C:\Python27;C:\Python27\Lib;C:\Python27\DLLs`, `python-2.7.5.msi`,
            `Python-2.7.5`, `C:\Python27`, `C:\Python27\python.exe`, `numpy-MKL-1.7.1.win32-py2.7.exe`,
            `C:\Python27\Scripts\easy_install.exe`, `C:\Python27\Scripts\pip.exe`,
            `C:\Python27\Scripts\virtualenv.exe`, `python27`,
            `C:\Python27\Lib\site-packages\numpy`, `C:\Unlock\python27\Lib\site-packages`,
            `C:\Unlock\python27\Scripts\python.exe`, `C:\Unlock\python27\Scripts\pip.exe`,
            `pyglet-1.2alpha1-p3.3.zip`, `pyglet-1.2alpha`, `pyglet-1.2alpha1`, `AVbin10-win32.exe`, 
            `pyserial-2.6.zip`, `pyserial-2.6`, `pyserial-2.6`, `unlock-0.3.7-win32.zip`, `unlock`, `unlock-0.3.7`,
            `scons-2.3.0.zip`, `scons`, `scons-2.3.0`}
    } else {
        return ParseConf(*confFile)
    }    
}

func numpyHack(pythonPath string, from string, to string) {
    var copydir = "import shutil\n"
    copydir += "import os\n"
    copydir += `shutil.copytree('`+from+`','`+to+`')`+"\n"
    fmt.Println(copydir)
    command := pythonPath+` -c '`+copydir+`'`
    runCommand(command, "numpyHack Failed", false)
}

func main() {

    flag.Parse()
    logf, err := os.OpenFile(`unlock-install.log`, os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }
    
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    log.Printf("conf file = "+*confFile)
    
    var conf = createConf()
    
    installPython(conf.BaseUrl, conf.PythonPathEnvVar, conf.PythonInstallerName, conf.PythonBasePath, conf.PythonPackageName)
    installNumPy(conf.BaseUrl, conf.NumpyPackageName)
    //installEasyInstall(conf.BaseUrl, conf.PythonPath)
    //installPip(conf.EasyInstallPath)
    //installVirtualenv(conf.PipPath)
    installAvbin(conf.BaseUrl, conf.Avbin)
    
    if err := os.MkdirAll(conf.UnlockDirectory, 0755); err != nil {
        log.Fatalln(`Failed to create `+conf.UnlockDirectory, err)
    }
    //createVirtualenv(conf.UnlockDirectory, conf.VirtualenvPath, conf.EnvName)
    // XXX - this is a hack for numpy.  on my machine the virtual env does the right thing, but on other machines it does not.
    //       I found this solution on stackoverflow; its not the best as it does register numpy with pip, but it does work for
    //       now.
    //numpyHack(conf.EnvPythonPath, conf.NumpyHack, conf.NumpyHack1)

    installPyglet12alpha(conf.PythonPath, conf.BaseUrl, conf.PygletZipName, conf.PygletPackageName, conf.PygletDirectory)
    installPySerial26(conf.PythonPath, conf.BaseUrl, conf.PyserialZipName, conf.PyserialPackageName, conf.PyserialDirectory)
    installUnlock(conf.PythonPath, conf.BaseUrl, conf.UnlockZipName, conf.UnlockPackageName, conf.UnlockPackageDirectory)
    installScons(conf.PythonPath, conf.BaseUrl, conf.SconsZipName, conf.SconsPackageName, conf.SconsPackageDirectory)
}
