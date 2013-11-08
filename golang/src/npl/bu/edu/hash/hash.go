package main

import (
    "flag"
    "log"    
    "npl/bu/edu/hashutil"
)

func main() {
    flag.Parse()
    
    file := flag.Arg(0)
    
    if file != `` {
        hashutil.WriteChecksum(file)
    } else {
        log.Fatalln("No file provided")
    }
}