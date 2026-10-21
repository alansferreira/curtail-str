package main

import (
	"fmt"

	abbrev "github.com/alansferreira/abbrev/packages/go"
)

func main() {
	result, err := abbrev.Abbrev("codigo-do-cliente")
	if err != nil {
		panic(err)
	}
	if result != "cdg-clnt" {
		panic("external Go consumer failed")
	}
	fmt.Println("External Go consumer OK")
}
