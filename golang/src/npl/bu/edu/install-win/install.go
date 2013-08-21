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

/////////////////////////////////////////////////////////////////////////

var base_url = `http://jpercent.org/`

func downloadAndWrite(url_name string, file_name string) {
    resp, err := http.Get(url_name)
    if err != nil {
        log.Fatalln(err)
    }
    defer resp.Body.Close()
    body, err1 := ioutil.ReadAll(resp.Body)
    if err1 = ioutil.WriteFile(file_name, body, 0744); err1 != nil {
        log.Fatalln(err1)
    }
}

func cwdAbs() string {
    cwd, err := filepath.Abs(``)
    log.Println(`Current working directory = `, cwd)
    if err != nil {
        log.Fatalln(err)
    }
    return cwd
}
/*
func checkForPython() error {
    log.Println(`Checking for Python...`)
    cmd := exec.Command(`cmd`, `/C C:\\Python27\\python.exe`)
    return cmd.Run()
}
*/

func installExe(exe_name string, package_name string, fail_on_error bool, post_fn func()) {
    log.Println(`Installing `+package_name+`...`)
    cwd := cwdAbs()
    cmd3 := exec.Command("cmd", "/C "+cwd+"\\"+exe_name)
    if err := cmd3.Run(); err != nil {
        if fail_on_error == true {
            log.Fatalln(`Failed installation of `+exe_name, err)
        } else {
            log.Println(`Did not install `+exe_name+` trying to continue`, err)
        }
    }
    post_fn()
    fmt.Println(`Successfully installed `+package_name)
}

func chdirFailOnError(directory string, error_msg string) {
    if err := os.Chdir(directory); err != nil {
        log.Fatalln(`install-win.chdirFailOnError: ERROR: Change directory to `+directory+` failed: `+error_msg, err)
    }
}

func unzipExpand(file_name string) {
    u := &unzip.Unzip{file_name, ``, nil}
    if err := u.Expand(); err != nil {
        log.Fatalln(`Failed to expand `+file_name, err)
    }    
}

func installZippedPythonPackage(file_name string, package_name string, local_dir string, post_fn func()) {
    log.Println(`Downloading `+package_name+`... `)
    downloadAndWrite(base_url+file_name, file_name)
    log.Println(`Installing `+package_name+`... `)
    unzipExpand(file_name)
    chdirFailOnError(local_dir, `Failed to install `+package_name)

    cmd2 := exec.Command(`cmd`, `/C C:\Python27\python.exe setup.py install`)
    if err := cmd2.Run(); err != nil {
        log.Fatalln(`Failed to install `+package_name, err)
    }
    post_fn()
    os.Chdir(`..`)
    log.Println(`Successfully installed `+package_name)
}

func installPython27(base_python_path string) {
    python_msi := `python-2.7.5.msi`
    package_name := `Python-2.7.5`
    command := `msiexec /i ` + python_msi + ` TARGETDIR=`+base_python_path+` /qb ALLUSERS=0 `
    log.Println(`Downloading `+package_name+`...`)
    downloadAndWrite(base_url+python_msi, python_msi)        
    post_fn := func() {}
    installExe(command, package_name, false, post_fn)
}

func configureDistribute() {
    distribute := `distribute_setup.py`
    downloadAndWrite(base_url+distribute, distribute)
}

func runExeNoPostProcessingFailOnError(command string, package_name string) {
    installExe(command, package_name, true, func() {})    
}

func installEasyInstall(python_path string) {
    command := python_path+` distribute_setup.py`
    runExeNoPostProcessingFailOnError(command, `easy_install`)
}

func installPip(easy_install_path string) {
//    command := `C:\Python27\Scripts\easy_install.exe pip`
    command := easy_install_path+` pip`
    runExeNoPostProcessingFailOnError(command, `pip`)
}

func installVirtualenv(pip_path string) {
    // `C:\Python27\Scripts\pip.exe install virtualenv`
    command := pip_path+` install virtualenv`
    runExeNoPostProcessingFailOnError(command, `virtualenv`)
}

func createVirtualenv(virtualenv_path string, envname string) {
    directory := `C:\Unlock`
    error_msg := `Failed to create virtual environment`
    chdirFailOnError(directory, error_msg)
//    command := `c:\Python27\Scripts\virtualenv.exe +` --distribute python27`    
    command := virtualenv_path+` --distribute `+envname //python27`
    runExeNoPostProcessingFailOnError(command, error_msg)
}

func installPyglet12alpha() {
    post_fn := func() {}
    installZippedPythonPackage(`pyglet-1.2alpha.zip`, `pyglet-1.2alpha`, `pyglet-1.2alpha1`, post_fn)
}

func installNumPy171() {
    post_fn := func() {}
    installExe(`numpy-MKL-1.7.1.win32-py2.7.exe`, `NumPy-1.7.1`, true, post_fn)
}

func installPySerial26() {
    post_fn := func() {}
    installZippedPythonPackage(`pyserial-2.6.zip`, `pyserial-2.6`, `pyserial-2.6`, post_fn)
}

func installUnlock() {
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
}

func main() {
    logf, err := os.OpenFile(`unlock-install.log`, os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    base_python_directory := `C:\Python27`
    python_path := base_python_directory + `python.exe `
    easy_install_path := base_python_directory + `\Scripts\easy_install.exe `
    pip_path := base_python_directory + `\Scripts\pip.exe `
    virtualenv_path := base_python_directory + `\Scripts\virtualenv.exe `
    
    installPython27(base_python_directory)
    configureDistribute()
    installEasyInstall(python_path)
    installPip(easy_install_path)
    installVirtualenv(pip_path)
    createVirtualenv(virtualenv_path, `python27`)
    
    installPyglet12alpha()
    installNumPy171()
    installPySerial26()
    installUnlock()
}
