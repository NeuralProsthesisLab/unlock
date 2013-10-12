
// Copyright (c) James Percent and Unlock contributors.
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

func downloadAndWriteFile(url string, fileName string) string {	
    // Get full path to file
    filePath := filepath.Join(getDownloadDirectory(), fileName)
    
	// Download if file not exists on disk
    isFileExist,_ := checkFileExists(filePath)
    if isFileExist == false {        
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
        
        if err = ioutil.WriteFile(filePath, body, 0744); err != nil {
            log.Fatalln(err)
        }
    }
    
    return filePath
}

func checkFileExists(path string) (bool, error) {
    _, err := os.Stat(path)
    if err == nil { return true, nil }
    if os.IsNotExist(err) { return false, nil }
    return false, err
}

func getDownloadDirectory() string {
    // Default is current working directory
	path := getWorkingDirectoryAbsolutePath()
    
    // If repoPath is specified, take the repo's "package" dir
	if *repoPath != `` {
		path = filepath.Join(*repoPath, `package`)
	}
    
    return path
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
    filePath := downloadAndWriteFile(baseUrl+fileName, fileName)
	
	unzipExpand(filePath)
    chdirFailOnError(packageDirectory, `Failed to install `+packageName)
    log.Println("CWD = "+getWorkingDirectoryAbsolutePath())
    command := pythonPath+` setup.py install`
    install(command, packageName, true)
    os.Chdir(`..`)
}

func installPython(baseUrl string, pythonPathEnvVar string, pythonInstallerName string, pythonBasePath string, pythonPackageName string) {
    //cwd := getWorkingDirectoryAbsolutePath()
    log.Println(`Downloading `+pythonPackageName+`...`)
    filePath := downloadAndWriteFile(baseUrl+pythonInstallerName, pythonInstallerName)
    log.Println(`Installing `+pythonPackageName)
//    output, err := exec.Command("cmd", "/C", "msiexec /i ", cwd+"\\"+pythonInstallerName,`TARGETDIR=`+pythonBasePath,`/qb`, `ALLUSERS=0`).CombinedOutput()
    //output, err := exec.Command("cmd", "/C", cwd+"\\"+pythonInstallerName).CombinedOutput()
    output, err := exec.Command("cmd", "/C", filePath).CombinedOutput()
    if len(output) > 0 {
        log.Printf("%s\n", output)
    }
    
    if err != nil {
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
    /*downloadAndWriteFile(baseUrl+numpyPath, numpyPath)//numpy-MKL-1.7.1.win32-py2.7.exe)
    var cwd = getWorkingDirectoryAbsolutePath()
    install(cwd+"\\"+numpyPath, `numpy`, true)*/
    
    installBinPackage(baseUrl, numpyPath, `numpy`)
}

func installBinPackage(baseUrl string, fileName string, packageName string) {
    filePath := downloadAndWriteFile(baseUrl+fileName, fileName)
    install(filePath, packageName, true)
}

func installPySerial26(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory);
}

func installAvbin(baseUrl string, avbin string) {
    /*downloadAndWriteFile(baseUrl+avbin, avbin)
    var cwd = getWorkingDirectoryAbsolutePath()
    install(cwd+"\\"+avbin, `avbin`, true)*/
    
    installBinPackage(baseUrl, avbin, `avbin`)
    
    // XXX - last minute hack
    data, err1 := ioutil.ReadFile(`C:\Windows\System32\avbin.dll`)
    if err1 != nil {
        log.Fatalln(err1)
    }
    
    if err := ioutil.WriteFile(`C:\Windows\SysWOW64\avbin.dll`, data, 0744); err != nil {
        log.Println(err)
    }    
    
}

func installScons(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory);
}

func installUnlock(pythonPath string, baseUrl string, fileName string, packageName string, packageDirectory string) {
    installZippedPythonPackage(pythonPath, baseUrl, fileName, packageName, packageDirectory)
}

var confFile = flag.String("conf", "", "Qualified file name of Unlock installation configuration file")
var devOption = flag.Bool("dev", false, "Setup development env")
var repoPath = flag.String("repo", "", "Path to project's git repo")

func createConf() UnlockInstallConf {
    if *confFile == `` {
        return UnlockInstallConf {`C:\Unlock`, `http://jpercent.org/unlock/`, `C:\Python33;C:\Python33\Lib;C:\Python33\DLLs`, `python-3.3.2.msi`,
            `Python-3.3.2`, `C:\Python33`, `C:\Python33\python.exe`, `numpy-MKL-1.7.1.win32-py3.3.exe`,
            `C:\Python33\Scripts\easy_install.exe`, `C:\Python33\Scripts\pip.exe`,
            `C:\Python33\Scripts\virtualenv.exe`, `python33`,
            `C:\Python33\Lib\site-packages\numpy`, `C:\Unlock\python33\Lib\site-packages`,
            `C:\Unlock\python33\Scripts\python.exe`, `C:\Unlock\python33\Scripts\pip.exe`,
            `pyglet-1.2alpha-p3.zip`, `pyglet-1.2alpha`, `pyglet-1.2alpha1`, `AVbin10-win32.exe`, 
            `pyserial-2.6.zip`, `pyserial-2.6`, `pyserial-2.6`, `unlock-0.3.7-win32.zip`, `unlock`, `unlock-0.3.7`,
            `scons-2.3.0.zip`, `scons`, `scons-2.3.0`,
            `unlock.exe`, `vcredist_2010_x86.exe`, `pyaudio-0.2.7.py33.exe`, `pywin32-218.win32-py3.3.exe`}
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

func installUnlockRunner(baseUrl string, unlockDirectory string, unlockexe string) {
    var cwd = getWorkingDirectoryAbsolutePath()
    chdirFailOnError(unlockDirectory, ` ERROR: Failed to install unlock.exe: couldn't change dir `)
    downloadAndWriteFile(baseUrl+unlockexe, unlockexe)
    os.Chdir(cwd)
}

func main() {

    flag.Parse()
    logf, err := os.OpenFile(`unlock-install.log`, os.O_WRONLY|os.O_APPEND|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }
    
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    log.Printf("conf file = "+*confFile)
    
    var conf = createConf()
    
    installPython(conf.BaseUrl, conf.PythonPathEnvVar, conf.PythonInstallerName, conf.PythonBasePath, conf.PythonPackageName)
    installBinPackage(conf.BaseUrl, conf.VCRedistPackageName, `vcredist`)
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
    installBinPackage(conf.BaseUrl, conf.PyAudioPackageName, `pyaudio`)
    installBinPackage(conf.BaseUrl, conf.PyWinPackageName, `pywin`)
	
	// Skip install unlock software for development option
	if *devOption == false {
        installUnlock(conf.PythonPath, conf.BaseUrl, conf.UnlockZipName, conf.UnlockPackageName, conf.UnlockPackageDirectory)
        //installScons(conf.PythonPath, conf.BaseUrl, conf.SconsZipName, conf.SconsPackageName, conf.SconsPackageDirectory)
        //installUnlockRunner(conf.BaseUrl, conf.UnlockDirectory, conf.Unlockexe)
	}
}
