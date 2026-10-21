# Abbreviate para Go

Go 1.26 ou superior. Dependencia de runtime: `golang.org/x/text/unicode/norm`
para normalizacao Unicode.

```go
package main

import (
    "fmt"
    "log"
    abbreviate "github.com/alansferreira/abbreviate/packages/go"
)

func main() {
    maximum := int64(2)
    result, err := abbreviate.EncurtarChaveUniversal("cliente", abbreviate.Options{
        Mode: abbreviate.Configurable,
        MaxWordLength: &maximum,
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result) // cl
}
```

Uma chamada sem `Options` usa `Universal`. O valor zero de `Options.Mode`
tambem significa universal. O modo `Custom` aceita
`Replacements: map[string]string{"the": "", "code": "cdg"}`. Mapa `nil`
significa ausente; mapa vazio nao nulo e fornecido e e rejeitado em universal.

`MinWordLength` (3), `PreserveWordLength` (3) e `MaxWordLength` (4) sao
ponteiros opcionais para `int64`, limitados a 1..2147483647. Sao independentes
e exclusivos de `Configurable`. Palavras preservadas e valores literais do
mapa nao sao truncados. `""` como substituicao remove o termo.

Erros de opcoes ou UTF-8 invalido retornam `error`, mesmo para entrada vazia.
Uma string vazia retorna `""` sem erro quando as opcoes sao validas.
Nenhum argumento e modificado; nao alterar mapas concorrentemente durante
uma chamada.

Nao ha traducao nem garantia de unicidade. `code` vira `cd` e `the` permanece
`the` por padrao. Comprimentos usam pontos de codigo Unicode.

Desenvolvimento: `go test -race ./...` e `go vet ./...`. Testes usam o corpus
da raiz do monorepositorio; consumidores nao dependem dele. Ate a publicacao
do repositorio, consumir com um `replace` local.
