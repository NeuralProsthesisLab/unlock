package main

import (
    "flag"
    "npl/bu/edu/chunker"
)

func main() {
    flag.Parse()
    
    file := flag.Arg(0)
    chunker.Chunk(file)
}