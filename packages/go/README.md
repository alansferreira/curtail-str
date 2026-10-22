# curtail-str for Go

Requires Go 1.26 or later. Uses `golang.org/x/text/unicode/norm` for Unicode
normalization.

## Install from source

Inside the consuming module, point the module path at a local checkout:

```sh
go mod edit -replace github.com/alansferreira/curtail-str/packages/go=/path/to/curtail-str/packages/go
go get github.com/alansferreira/curtail-str/packages/go
```

## Usage

```go
package main

import (
    "fmt"
    "log"
    curtailstr "github.com/alansferreira/curtail-str/packages/go"
)

func main() {
    maximum := int64(2)
    result, err := curtailstr.CurtailStr("customer", curtailstr.Options{
        Mode: curtailstr.Configurable,
        MaxWordLength: &maximum,
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result) // cs
}
```

Calling without `Options` uses `Universal`. The zero value of `Options.Mode`
also means universal. `Custom` accepts, for example,
`Replacements: map[string]string{"the": "", "code": "cdg"}`.
A `nil` map means omitted; a non-nil empty map counts as supplied and is
rejected in universal mode.

`MinWordLength` (3), `PreserveWordLength` (3), and `MaxWordLength` (4) are
optional `*int64` values ranging from 1 through 2147483647. They are independent
and available only in `Configurable`. Preserved words and literal replacement
values are not truncated. An empty replacement removes a term.

Invalid options or invalid UTF-8 return an `error`, even for empty input.
Empty input returns `""` without error when options are valid.
Arguments are not mutated; do not modify maps concurrently during a call.

The heuristic does not translate words or guarantee uniqueness. By default,
`code` becomes `cd` and `the` remains `the`. Lengths use Unicode code points.

## Development

Run `go test -race ./...` and `go vet ./...` from this directory.
Tests use fixtures at the repository root; consumers do not depend on them.

See the [algorithm contract](https://github.com/alansferreira/curtail-str/blob/main/spec/algorithm.md) for complete semantics.
