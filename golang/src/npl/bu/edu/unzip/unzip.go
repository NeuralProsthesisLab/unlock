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