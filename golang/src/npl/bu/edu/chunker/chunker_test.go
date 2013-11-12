package chunker

import (
    "testing"
    "npl/bu/edu/util"
    "npl/bu/edu/hashutil"
    "os"
    "strconv"
    "path/filepath"
)

func TestChunker(t *testing.T) {
    testDir,_ := filepath.Abs("./test")
    testFile,_ := filepath.Abs(testDir+"/testfile")

    // Delete unwanted files if exists
    isExist,err := util.CheckFileExists(testDir)
    if err != nil {
        t.Error(err)
    }
    if (isExist) {
        err = os.RemoveAll(testDir)
        if err != nil {
            t.Error(err)
        }
    }    
    err = os.Mkdir(testDir, 0755)
    if err != nil {
        t.Error(err)
    }
    
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
    isExist,err = util.CheckFileExists(testFile+".sha1")
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
    
    // Clean up test files
    err = os.RemoveAll(testDir)
    if err != nil {
        t.Error(err)
    }
}