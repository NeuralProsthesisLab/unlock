package hashutil

import (
    "testing"
    "os"
    "npl/bu/edu/testutil"
)

func TestHash(t *testing.T) {
    testFile := testutil.Setup(t)
    
    // Create file
    fo, err := os.Create(testFile)
    if err != nil { t.Error(err) }    
    buf := make([]byte, 1000)
    if _, err = fo.Write(buf); err != nil {
        t.Error(err)
    }
    if err = fo.Close(); err != nil {
        t.Error(err)
    }
    
    // Write checksum
    WriteChecksum(testFile)
    
    // Compare checksum
    isMatch := CompareChecksum(testFile)
    if (!isMatch) {
        t.Error("Computed checksum not match")
    }
    
    testutil.Teardown(t)
}