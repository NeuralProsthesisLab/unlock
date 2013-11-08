package main

import (
    "flag"
    "npl/bu/edu/chunker"
)

var reconstruct = flag.Bool(`r`, false, `Reconstruct file instead of chunking`)

func main() {
    flag.Parse()    
    file := flag.Arg(0)
    
    if !*reconstruct {
        chunker.Chunk(file)
    } else {
        chunker.Reconstruct(file)
    }
}