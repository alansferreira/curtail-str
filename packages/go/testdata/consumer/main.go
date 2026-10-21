package main

import (
	"fmt"

	curtailstr "github.com/alansferreira/curtail-str/packages/go"
)

func main() {
	result, err := curtailstr.CurtailStr("codigo-do-cliente")
	if err != nil {
		panic(err)
	}
	if result != "cdg-clnt" {
		panic("external Go consumer failed")
	}
	fmt.Println("External Go consumer OK")
}
