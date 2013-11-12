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