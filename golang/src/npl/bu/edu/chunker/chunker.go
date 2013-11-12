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

package chunker

import (
    "os"
    "strconv"
    "log"
    "io"
    "npl/bu/edu/util"
    "npl/bu/edu/hashutil"
)

func Chunk(path string) {
    fileinfo,err := os.Stat(path)
    if err != nil {
        panic(err)
    }
    
    if fileinfo.Size() < 100000000 {
        panic(`File must be 100MB or more`)
    }
    
    // Make sha1
    hashutil.WriteChecksum(path)
    
    // open input file
    fi, err := os.Open(path)
    if err != nil { panic(err) }
    // close fi on exit and check for its returned error
    defer func() {
        if err := fi.Close(); err != nil {
            panic(err)
        }
    }()

    readIndex := 0  
    i := 0
    for {
        // open output file
        fo, err := os.Create(path+`.part`+strconv.Itoa(i))
        if err != nil { panic(err) }
        // close fo on exit and check for its returned error
        defer func() {
            finfo,err := fo.Stat()
            if err != nil { panic(err) } 
        
            if err := fo.Close(); err != nil {
                panic(err)
            }            
                       
            if finfo.Size() == 0 {
                os.Remove(fo.Name())
            } else {
                hashutil.WriteChecksum(fo.Name())
            }
        }()

        // make a buffer to keep chunks that are read
        buf := make([]byte, 50000000)
        // read a chunk
        log.Println(`readIndex =`, readIndex)
        byteRead, err := fi.ReadAt(buf, int64(readIndex))    
        log.Println(`Read`, byteRead, `bytes`)
        // Somehow ReadAt() returns EOF != io.EOF so we have to manually compare like this
        if err != nil && err.Error() != `read `+fi.Name()+`: Reached the end of the file.` { panic(err) }
        if byteRead == 0 { break }

        // write a chunk
        log.Println(`Begin writing`)
        if _, err := fo.Write(buf[:byteRead]); err != nil {
            panic(err)
        }
        
        readIndex += byteRead        
        i++
    }
}

func Reconstruct(path string) {
    fileIsGood := false
    var i int
    for i = 0; i < 5 && !fileIsGood; i++ {
        reconstruct(path)
        fileIsGood = hashutil.CompareChecksum(path)
    }
    if i == 5 { log.Fatalln(`Failed to reconstruct`, path) }
}

func reconstruct(path string) {
    log.Println("Reconstruct file", path)
    
    // open output file
    fo, err := os.Create(path)
    if err != nil { panic(err) }
    // close fo on exit and check for its returned error
    defer func() {
        if err := fo.Close(); err != nil {
            panic(err)
        }
    }()

    writeIndex := 0  
    i := 0
    for {
        inFile := path+`.part`+strconv.Itoa(i)
    
        // Exit if no more part
        isFileExist,err := util.CheckFileExists(inFile)
        if err != nil { panic(err) }
        if !isFileExist { break }
    
        // open input file
        fi, err := os.Open(inFile)
        if err != nil { panic(err) }
        // close fi on exit and check for its returned error
        defer func() {
            if err := fi.Close(); err != nil {
                panic(err)
            }
        }()

        // make a buffer to keep chunks that are read
        buf := make([]byte, 50000000)
        // read a chunk
        byteRead, err := fi.Read(buf)    
        if err != nil && err != io.EOF { panic(err) }
        
        // write a chunk
        if _, err := fo.WriteAt(buf[:byteRead], int64(writeIndex)); err != nil {
            panic(err)
        }
        
        writeIndex += byteRead        
        i++
    }
} 