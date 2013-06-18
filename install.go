package main

import (
    "net/http"
    "fmt"
    "io/ioutil"
    "os"
    "os/exec"
    "log"
//    "time"
    "path/filepath"
    "io"
    "archive/zip"
    "container/list"
    "strings"
)

type Unzip struct {
    zipfile string
    prefix string
    artifacts *list.List
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
    if err := meta.walk(u.zipfile); err != nil {
        return err
    } else {
        u.artifacts = meta.artifacts
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
    if err := meta.walk(u.zipfile); err != nil {
        return err
    } else {
        u.artifacts = meta.artifacts
    }
    return nil
}

func (u *Unzip) Expand() error {
    file_handler := func (meta *ZipMeta) error {

        if meta.artifacts == nil {
            meta.artifacts = list.New()
        }
        zipfile := meta.current_file.file
        meta.artifacts.PushBack(meta.current_file)

        var (
            err error
            file *os.File
            rc io.ReadCloser
        )
        if rc, err = zipfile.Open(); err != nil {
            return err
        }

        if file, err = os.Create(zipfile.Name); err != nil {
            return err
        }

        if _, err = io.Copy(file, rc); err != nil {
            return err
        }

        if err = file.Chmod(zipfile.Mode().Perm()); err != nil {
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
    if err := meta.walk(u.zipfile); err != nil {
        return err
    } else {
        u.artifacts = meta.artifacts
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

func (w *ZipMeta) walk(zipfile string) error {
    var err error
    var r *zip.ReadCloser
    if r, err = zip.OpenReader(zipfile); err != nil {
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

/////////////////////////////////////////////////////////////////////////

func downloadAndWrite(url_name string, file_name string) {
    resp, err := http.Get(url_name)
    if err != nil {
        log.Fatalln(err)
    }
    defer resp.Body.Close()
    body, err1 := ioutil.ReadAll(resp.Body)
    if err1 = ioutil.WriteFile(file_name, body, 0744); err1 != nil {
        log.Fatalln(err1)
    }
}

func getPath() string {
    path, err := filepath.Abs("")
    fmt.Println("path = ", path)
    if err != nil {
        log.Fatalln(err)
    }
    return path
}

func checkForPython() error {
    log.Println("Checking for Python...")
    cmd := exec.Command("cmd", "/C C:\\Python27\\python.exe")
    return cmd.Run()
}

func installPython(path string) {
    log.Println("Installing Python...")
    cmd := exec.Command("cmd", "/C "+path+"\\python-2.7.5.msi")
    if err := cmd.Run(); err != nil {
        log.Fatalln("Failed to install Python ", err)
    }
}

func setupPython() {
    if err := checkForPython(); err != nil {
        log.Println("Downloading Python...")
        downloadAndWrite("http://jpercent.org/python-2.7.5.msi", "python-2.7.5.msi")
        path := getPath()
        installPython(path)
        log.Println("Successfully installed Python")
    } else {
        log.Println("Python is already installed")
    }
}



func installNumpy() {
    log.Println("Downloading NumPy...")
    downloadAndWrite("http://jpercent.org/numpy-MKL-1.7.1.win32-py2.7.exe", "numpy-MKL-1.7.1.win32-py2.7.exe")
    log.Println("Installing NumPy...")
    path := getPath()
    cmd3 := exec.Command("cmd", "/C "+path+"\\numpy-MKL-1.7.1.win32-py2.7.exe")
    if err := cmd3.Run(); err != nil {
        log.Fatalln(err)
    }
    fmt.Println("Successfully installed NumPy")
}

var base_url = "http://jpercent.org/"

func installZippedPythonPackage(file_name string, package_name string, local_dir string, post_fn func()) {
    log.Println("Downloading "+package_name+"... ")
    downloadAndWrite(base_url+file_name, file_name)
    log.Println("Installing "+package_name+"... ")
    u := &Unzip{file_name, "", nil}
    if err := u.Expand(); err != nil {
        log.Fatalln("Failed to expand "+file_name, err)
    }

    if err := os.Chdir(local_dir); err != nil {
        log.Fatalln("Downloading and/or installing "+package_name+" failed ", err)
    }
    cmd2 := exec.Command("cmd", "/C C:\\Python27\\python.exe setup.py install")
    if err := cmd2.Run(); err != nil {
        log.Fatalln("Failed to install "+package_name, err)
    }
    post_fn()
    if err := os.Chdir(".."); err != nil {
        // ...
    }
    log.Println("Successfully installed "+package_name)
}

func installPyglet12alpha() {
    post_fn := func() {}
    file_name = "pyglet-1.2alpha.zip"
    package_name = "pyglet-1.2alpha"
    local_dir = "pyglet-1.2alpha1"
    installZippedPythonPackage(file_name, package_name, local_dir, post_fn)
}

func installPySerial26() {
    post_fn := func() {}
    file_name = "pyserial-2.6.zip"
    package_name = "pyserial-2.6"
    installZippedPythonPackage(file_name, package_name, package_name, post_fn)
}

func installUnlock() {
    post_processing_fn := func() {
        if err := os.MkdirAll("C:\\Unlock", 0755); err != nil {
            log.Fatalln("Failed to make unlock directory", err)
        }
        if err := os.Rename("collector.py", "C:\\Unlock\\collector.py"); err != nil {
            log.Fatalln("Failed to install unlock collector", err)
        }

        if err := os.Rename("collector.bat", "C:\\Unlock\\collector.bat"); err != nil {
            log.Fatalln("Failed to install unlock collector", err)
        }

        if err := os.Rename("pygtec.py", "C:\\Unlock\\pygtec.py"); err != nil {
            log.Fatalln("Failed to install unlock collector", err)
        }

        if err := os.Rename("targets.png", "C:\\Unlock\\targets.png"); err != nil {
            log.Fatalln("Failed to install unlock collector", err)
        }
    }
    installZippedPythonPackage("unlock.zip", "unlock", "unlock-npl", post_processing_fn)
}

func main() {
    logf, err := os.OpenFile("unlock-install.log", os.O_WRONLY|os.O_CREATE,0640)
    if err != nil {
        log.Fatalln(err)
    }
    log.SetOutput(io.MultiWriter(logf, os.Stdout))
    //setupPython()
    installPyglet12alpha()
    installNumpy()
    installPySerial26()
    installUnlock()
}
