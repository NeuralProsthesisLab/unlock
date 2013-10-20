package main

import (
    "io/ioutil"
    "flag"
    "log"
    "crypto/sha1"
    "path/filepath"
)

var file = flag.String("file", "", "File to hash")

func main() {
    flag.Parse()
    
    if *file != `` {
        fullPath,_ := filepath.Abs(*file)
        log.Println("Full path: " + fullPath)
    
        hash := computeChecksum(fullPath)
        
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

func computeChecksum(filePath string) []byte {
    content,err := ioutil.ReadFile(filePath)
    if err != nil { panic(err) }
    
    s1 := sha1.New()
    s1.Write([]byte(content))
    hashed := s1.Sum(nil)
    
    log.Println(`Computed checksum: `, hashed)
    
    return hashed
}