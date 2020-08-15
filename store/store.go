package store

import (
    "path/filepath"
    "io/ioutil"
    "os"
)

type FilesystemStore struct {
	Root string
}

func (s FilesystemStore) Write(name string, buffer []byte) (dst string, err error) {
    outPath := filepath.Join(s.Root, name)

    f, err := os.OpenFile(outPath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0666)
    if err != nil {
        return outPath, err
    }

    _, err = f.Write(buffer)
    return outPath, err
}

func (s FilesystemStore) Read(name string) (buffer []byte, err error) {
	return ioutil.ReadFile(name)
}