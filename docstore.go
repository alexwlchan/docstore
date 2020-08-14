package main

import (
  "fmt"
  "io/ioutil"
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

func Read(s Store) error {
  return s.Write("hello.txt", []byte("hello world\n"))
}

func main() {
  s := FilesystemStore { root: "." }
  err := Read(s)
  fmt.Println(err)
  data, _ := s.Read("hello.txt")
  fmt.Println(string(data))
	fmt.Println("Hello, 世界")
}
