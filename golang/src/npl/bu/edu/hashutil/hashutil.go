// Copyright (c) Giang Nguyen, James Percent and Unlock contributors.
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