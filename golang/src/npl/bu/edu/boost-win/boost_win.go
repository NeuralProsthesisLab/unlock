package main

import (
    "npl/bu/edu/unzip"
    "os"
    "os/exec"
    "log"
    "path/filepath"
    "io"
)

func cwdAbs() string {
    cwd, err := filepath.Abs("")
    if err != nil {
        log.Fatalln(err)
    }
    return cwd
}

func main() {
    logf, err := os.OpenFile("boost-win.log", os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln("Failed to create boost-win.log", err)
    }
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    
    log.Println(" Version 0.91 ")

    u := &unzip.Unzip{"boost_1_54_0.zip", "", nil}
    if err := u.Expand(); err != nil {
        log.Fatalln("Failed to expand boost_1_54_0.zip ", err)
    }

    boost_dir := cwdAbs()
    
    if err := os.Chdir("boost_1_54_0"); err != nil {
        log.Fatalln("Failed to build Boost; the directory boost_1_54_0 does not exist ", err)
    }

    build_dir := cwdAbs()
   bootstrap_cmd := "/C "+build_dir+"\\"+"bootstrap"
   log.Println("Executing: "+bootstrap_cmd)
    cmd := exec.Command("cmd", bootstrap_cmd)
    if err := cmd.Run(); err != nil {
        log.Fatalln("Failed to execute boostrap command: "+bootstrap_cmd, err)
    }
    log.Println("Success: "+bootstrap_cmd)

    b2_cmd :=  "/C "+build_dir+"\\"+"b2 install --prefix="+boost_dir+"\\win-x86  address-model=32  runtime-link=shared link=shared"
    log.Println("Executing: "+b2_cmd)    
    cmd = exec.Command("cmd", b2_cmd)
    if err := cmd.Run(); err != nil {
        log.Fatalln("Failed to execute b2: ", err)
    }

}
