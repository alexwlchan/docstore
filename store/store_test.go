package store_test

import (
    "docstore.alexwlchan.net/store"
    "os"
    "io/ioutil"
    "strings"
    "testing"
)

func CreateFilesystemStore(t *testing.T) (store.FilesystemStore, func()) {
    root, err := ioutil.TempDir("", "")

    if err != nil {
        t.Fatal(err)
    }

    s := store.FilesystemStore{ Root: root }

    return s, func() {
        err := os.RemoveAll(root)
        if err != nil {
            t.Error(err)
        }
    }
}

func TestWrite(t *testing.T) {
    s, cleanup := CreateFilesystemStore(t)
    defer cleanup()

    testBytes := []byte("Hello world\n")

    dst, err := s.Write("hello.txt", testBytes)
    if err != nil {
        t.Fatal(err)
    }

    if !strings.HasPrefix(dst, s.Root) {
        t.Errorf("Store has root %s, Write() wrote file to %s", s.Root, dst)
    }

    file, err := os.Open("file.txt")
    if err != nil {
        t.Fatal(err)
    }

    b, err := ioutil.ReadAll(file)
    if b != testBytes {
        t.Errorf("Expected Store to Write %s, actually wrote %s", testBytes, b)
    }
}
