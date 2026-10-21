package main

import (
	"fmt"

	abrev "github.com/alansferreira/abrev/packages/go"
)

func main() {
	result, err := abrev.Abrev("codigo-do-cliente")
	if err != nil {
		panic(err)
	}
	if result != "cdg-clnt" {
		panic("external Go consumer failed")
	}
	fmt.Println("External Go consumer OK")
}
