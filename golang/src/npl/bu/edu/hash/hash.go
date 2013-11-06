package main

import (
    "io/ioutil"
    "flag"
    "log"
    "path/filepath"
    "npl/bu/edu/hashutil"
)

func main() {
    flag.Parse()
    
    file := flag.Arg(0)
    
    if file != `` {
        fullPath,_ := filepath.Abs(file)
        log.Println("Full path: " + fullPath)
    
        hash := hashutil.ComputeChecksum(fullPath)
        
        hashFile := fullPath + ".sha1"
        err := ioutil.WriteFile(hashFile, hash, 0755)
        if err != nil {
            log.Fatalln(err)
        }
        
        data, err := ioutil.ReadFile(hashFile)
        if err != nil {
            log.Fatalln(err)
        } else {
            log.Println("File reads:", data)
        }
    } else {
        log.Fatalln("No file provided")
    }
}