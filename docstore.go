package main

import (
    "bytes"
  "fmt"
  "io"
  "io/ioutil"
  "filippo.io/age"
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
    r.SetWorkFactor(15)

    f, err := os.Create(name)

    if err != nil {
        return err
    }

    buf := &bytes.Buffer{}
    w, err := age.Encrypt(f, r)
    if err != nil {
        return err
    }

    if _, err = io.WriteString(w, "Hello world"); err != nil {
        return err
    }

    fmt.Println(buf)

    return nil
}

func main() {
  s := EncryptedFilesystemStore { root: "." }
  s.Write("greeting.txt", []byte("hello world\n"), "password123")
  // data, _ := s.Read("hello.txt")
  // fmt.Println(string(data))
    // fmt.Println("Hello, 世界")
}
