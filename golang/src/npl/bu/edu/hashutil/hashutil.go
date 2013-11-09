package hashutil

import (
    "crypto/sha1"
    "io/ioutil"
    "log"
    "path/filepath"
    "bytes"
)

func ComputeChecksum(filePath string) []byte {
    content,err := ioutil.ReadFile(filePath)
    if err != nil { panic(err) }
    
    s1 := sha1.New()
    s1.Write([]byte(content))
    hashed := s1.Sum(nil)
    
    log.Println(`Computed checksum: `, hashed)
    
    return hashed
}

func WriteChecksum(file string) {
    fullPath,_ := filepath.Abs(file)
    log.Println("Full path: " + fullPath)
    
    hash := ComputeChecksum(fullPath)
        
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
}

func CompareChecksum(path string) bool {
    content,err := ioutil.ReadFile(path+`.sha1`)
    if err != nil { panic(err) }
    
    result := bytes.Compare(ComputeChecksum(path), content) == 0
    if !result { log.Println("Checksum not match") } else { log.Println("Checksum match") }
    
    return result
}