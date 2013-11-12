package testutil

import (
    "testing"
    "path/filepath"
    "os"
    "npl/bu/edu/util"
)
    
func Setup(t *testing.T) string {
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
    
    return testFile
}

func Teardown(t *testing.T) {
    // Clean up test files
    testDir,_ := filepath.Abs("./test")
    err := os.RemoveAll(testDir)
    if err != nil {
        t.Error(err)
    }
}