package hashutil

import (
    "crypto/sha1"
    "io/ioutil"
    "log"
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