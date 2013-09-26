
// Copyright (c) James Percent and Unlock contributors.
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

package unzip

import (
    "os"
    "log"
    "io"
    "archive/zip"
    "container/list"
    "strings"
)

type Unzip struct {
    Zipfile string
    Prefix string
    Artifacts *list.List
}

type ZipArtifact struct {
  name string
  path string
  file *zip.File
}

func (u *Unzip) PrintListing() error {
    file_handler := func (meta *ZipMeta) error {
        log.Println(meta.current_file.path + meta.current_file.name)
        return nil
    }

    folder_handler := func(meta *ZipMeta) error {
        return nil
    }
    meta := ZipMeta { file_handler, folder_handler, make(map[string]bool), "", nil, nil} //list.New(), 1,true}
    if err := meta.walk(u.Zipfile); err != nil {
        return err
    } else {
        u.Artifacts = meta.artifacts
    }
    return nil
}

func (u *Unzip) GenerateListing() error {
    file_handler := func (meta *ZipMeta) error {
        if meta.artifacts == nil {
            meta.artifacts = list.New()
        }
        meta.artifacts.PushBack(meta.current_file)
        return nil
    }

    folder_handler := func(meta *ZipMeta) error {
        return nil
    }
    meta := ZipMeta { file_handler, folder_handler, make(map[string]bool), "", nil, nil}
    if err := meta.walk(u.Zipfile); err != nil {
        return err
    } else {
        u.Artifacts = meta.artifacts
    }
    return nil
}

func (u *Unzip) Expand() error {
    file_handler := func (meta *ZipMeta) error {

        if meta.artifacts == nil {
            meta.artifacts = list.New()
        }
        Zipfile := meta.current_file.file
        meta.artifacts.PushBack(meta.current_file)

        var (
            err error
            file *os.File
            rc io.ReadCloser
        )
        if rc, err = Zipfile.Open(); err != nil {
            return err
        }

        if file, err = os.Create(Zipfile.Name); err != nil {
            return err
        }

        if _, err = io.Copy(file, rc); err != nil {
            return err
        }

        if err = file.Chmod(Zipfile.Mode().Perm()); err != nil {
            //log.Println(err) // Windows WTF?
        }
        file.Close()
        rc.Close()
        return nil
    }

    folder_handler := func(meta *ZipMeta) error {
        return os.MkdirAll(meta.last_folder, 0755)
    }
    meta := ZipMeta {file_handler, folder_handler, make(map[string]bool), "", nil, nil}
    if err := meta.walk(u.Zipfile); err != nil {
        return err
    } else {
        u.Artifacts = meta.artifacts
    }
    return nil
}

type ZipMeta struct {
    file_handler func(*ZipMeta) error
    folder_handler func(*ZipMeta) error
    folders map[string]bool
    last_folder string
    current_file *ZipArtifact
    artifacts *list.List
}

func (w *ZipMeta) isNewFolder(folder_name string) bool {
    _, found := w.folders[folder_name]
    return !found
}

func (w *ZipMeta) handleFile(path string, file_name string, file *zip.File) error {
    w.current_file = &ZipArtifact{file_name, path, file}
    return w.file_handler(w)
}

func (w *ZipMeta) handleFolder(folder_name string) error {
    w.folders[folder_name] = true
    w.last_folder = folder_name
    return w.folder_handler(w)
}

func (w *ZipMeta) walk(Zipfile string) error {
    var err error
    var r *zip.ReadCloser
    if r, err = zip.OpenReader(Zipfile); err != nil {
      log.Fatalln(err)
      return err
    }

    for _, f := range r.File {

      if f.Mode().IsDir() {
        w.handleFolder(f.Name)
        continue
      }

      file_name := f.Name
      folder_name := ""
      folder_index := strings.LastIndex(f.Name, "/")
      if folder_index != -1 {
        folder_name += file_name[:folder_index] // 4.4.17
        if w.isNewFolder(folder_name) {
            if err = w.handleFolder(folder_name); err != nil {
                return err
            }
        }
        file_name = file_name[folder_index+1:] // strings.Join(dirlist[:len(dirlist)-1]
      }

      if err = w.handleFile(folder_name, file_name, f); err != nil {
          return err
      }
    }
    r.Close()
    return nil
}