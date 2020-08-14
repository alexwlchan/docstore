package main

import (
    // "bufio"
  "fmt"
  "io"
  "io/ioutil"
  "filippo.io/age"
  // "filippo.io/age/armor"
  "os"
  // "path/filepath"
  )

type Store interface {
  Write(name string, buffer []byte) error
  Read(name string) (buffer []byte, err error)
}

type FilesystemStore struct {
  root string
}

func (s FilesystemStore) Write(name string, buffer []byte) error {
  return ioutil.WriteFile(name, buffer, 0644)
}

func (s FilesystemStore) Read(name string) (buffer []byte, err error) {
  return ioutil.ReadFile(name)
}

type EncryptedFilesystemStore struct {
    root string
}

func (efs EncryptedFilesystemStore) Write(name string, buffer []byte, password string) error {
    r, err := age.NewScryptRecipient(password)
    if err != nil {
        return err
    }
    // r.SetWorkFactor(15)

    // TODO: Consider using os.OpenFile to open the file exclusively
    f, err := os.OpenFile(name, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0666)

    if err != nil {
        return err
    }

    w, err := age.Encrypt(f, r)
    if err != nil {
        return err
    }


    if _, err = io.WriteString(w, "Hello world"); err != nil {
        return err
    }

    // If I don't call w.Close(), I get an "unexpected EOF" when trying to
    // decrypt the file.
    w.Close()
    f.Close()

    return nil
}

func (efs EncryptedFilesystemStore) Read(name string, password string) (buffer []byte, err error) {
    i, err := age.NewScryptIdentity(password)
    if err != nil {
        return nil, err
    }

    f, err := os.Open(name)
    if err != nil {
        return nil, err
    }
    // defer f.Close()

    outDe, err := age.Decrypt(f, i)
    if err != nil {
        return nil, err
    }

    // fmt.Println(outDe)

    outBytes, err := ioutil.ReadAll(outDe)
    if err != nil {
        fmt.Println("Error when calling ReadAll")
        return nil, err
    }

    return outBytes, nil
}

func main() {
  s := EncryptedFilesystemStore { root: "." }
  err := s.Write("greeting.txt.age", []byte("hello world\n"), "password123")
  fmt.Println(err)
  bytes, err := s.Read("greeting.txt.age", "password123")
  fmt.Println(string(bytes))
   fmt.Println(err)
  // data, _ := s.Read("hello.txt")
  // fmt.Println(string(data))
    // fmt.Println("Hello, 世界")
}
