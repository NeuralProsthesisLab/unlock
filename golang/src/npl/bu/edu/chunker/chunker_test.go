package chunker

import (
    "testing"
    "npl/bu/edu/util"
    "npl/bu/edu/hashutil"
    "npl/bu/edu/testutil"
    "os"
    "strconv"
)

func TestChunker(t *testing.T) {
    testFile := testutil.Setup(t)
    
    // Create 100MB file
    fo, err := os.Create(testFile)
    if err != nil { t.Error(err) }    
    buf := make([]byte, 100000000)
    if _, err = fo.Write(buf); err != nil {
        t.Error(err)
    }
    if err = fo.Close(); err != nil {
        t.Error(err)
    }

    // Chunk file
    Chunk(testFile)
    
    // Check if original sha1 created
    isExist,err := util.CheckFileExists(testFile+".sha1")
    if err != nil {
        t.Error(err)
    }
    if (!isExist) {
        t.Error("Original file's sha1 not created")
    }
    
    // Check if parts created
    for i := 0; i < 2; i++ {
        isExist,err := util.CheckFileExists(testFile+".part"+strconv.Itoa(i))
        if err != nil {
            t.Error(err)
        }
        if (!isExist) {
            t.Error("Part", i, "not created")
        }
    }
    
    // Delete original file
    err = os.Remove(testFile)
    if err != nil {
        t.Error(err)
    }
    
    // Reconstruct file
    Reconstruct(testFile)
    
    // Check original sha1
    isMatch := hashutil.CompareChecksum(testFile)
    if (!isMatch) {
        t.Error("Reconstructed file not match original sha1")
    }
    
    testutil.Teardown(t)
}