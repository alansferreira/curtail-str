package main

import (
	"fmt"

	abbreviate "github.com/alansferreira/abbreviate/packages/go"
)

func main() {
	result, err := abbreviate.EncurtarChaveUniversal("codigo-do-cliente")
	if err != nil {
		panic(err)
	}
	if result != "cdg-clnt" {
		panic("external Go consumer failed")
	}
	fmt.Println("External Go consumer OK")
}
