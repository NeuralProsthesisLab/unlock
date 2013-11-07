package chunker

import (
    "os"
    "io"
    "strconv"
)

func Chunk(path string) {
    fileinfo,err := os.Stat(path)
    if err != nil {
        panic(err)
    }
    
    if fileinfo.Size() < 100000000 {
        panic(`File must be 100MB or more`)
    }
    
    // open input file
    fi, err := os.Open(path)
    if err != nil { panic(err) }
    // close fi on exit and check for its returned error
    defer func() {
        if err := fi.Close(); err != nil {
            panic(err)
        }
    }()

    n := 1  
    i := 0
    for {
        // open output file
        fo, err := os.Create(path+`.part`+strconv.Itoa(i))
        if err != nil { panic(err) }
        // close fo on exit and check for its returned error
        defer func() {
            if err := fo.Close(); err != nil {
                panic(err)
            }
        }()

        // make a buffer to keep chunks that are read
        buf := make([]byte, 50000000)
        for {
            // read a chunk
            n, err = fi.ReadAt(buf, int64(n-1))
            if err != nil && err != io.EOF { panic(err) }
            if n == 0 { return }

            // write a chunk
            if _, err := fo.Write(buf[:n]); err != nil {
                panic(err)
            }
        }
        
        i++
    }
}

func Reconstruct(path string) {

}