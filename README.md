# curtail-str

Small, pure libraries for shortening identifiers in Node.js, Python, Go, and
Java. Each library implements the same dictionary-free algorithm with three
explicit modes.

```text
active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
codigo-do-cliente-ativo-no-estoque -> cdg-clnt-atv-estq
```

Words such as `code` become `cd`; three-character words such as `the` are
preserved. Use replacements to override individual words:
`{"the": "", "code": "cdg"}` produces `actv-cstm-cdg-stck` for the first input.

## Modes

| Mode | Behavior |
| --- | --- |
| `universal` | Default: discard words shorter than 3 characters, preserve words of length 3, compress longer words to at most 4 characters |
| `custom` | Apply an optional replacement map before the universal rules |
| `configurable` | Apply an optional replacement map and three independent length limits |

Compression preserves the first code point, removes vowels and their accents
from the remainder, collapses consecutive identical letters, and truncates.
Separators are ASCII hyphens, underscores, and Unicode whitespace. Input is
lowercased without locale-dependent rules and normalized to NFC. Lengths are
measured in Unicode code points. Other punctuation, numbers, and symbols remain.

Replacement values are **literal results**: they are not normalized, compressed,
or truncated. An empty value removes a word. Keys use the same normalization as
the input; empty keys, keys containing separators, and normalized collisions
are rejected.

Length options are available only in `configurable` mode. Replacement maps,
including empty maps, are not accepted in `universal` mode. Preserved words and
replacement values bypass truncation. Limits are independent integers from 1
through 2147483647.

Null or empty input produces an empty string when options are valid. Invalid
options always produce an explicit error. Go strings cannot be `nil`; use `""`.
See the [algorithm contract](./spec/algorithm.md) and
[shared test cases](./spec/cases.json) for details.

## Packages and compatibility

| Language | Minimum version | API and guide |
| --- | --- | --- |
| Node.js | 22 | [curtailStr](./packages/node/README.md), ESM/CommonJS and TypeScript declarations |
| Python | 3.11 | [curtail_str](./packages/python/README.md), typed package |
| Go | 1.26 | [CurtailStr](./packages/go/README.md), returns `(string, error)` |
| Java | 8, Eclipse Temurin | [CurtailStr.curtailStr](./packages/java/README.md), JAR without runtime dependencies |

| Option | Node.js / Java | Python | Go | Default |
| --- | --- | --- | --- | --- |
| Mode | `mode` | `mode` | `Mode` | universal |
| Replacements | `replacements` | `replacements` | `Replacements` | omitted |
| Minimum length | `minWordLength` | `min_word_length` | `MinWordLength` | 3 |
| Preservation length | `preserveWordLength` | `preserve_word_length` | `PreserveWordLength` | 3 |
| Compressed length | `maxWordLength` | `max_word_length` | `MaxWordLength` | 4 |

Java uses a `Mode` enum and immutable options built with a builder. Go uses
typed constants and optional pointers for length limits.

### Install from source

Clone the repository and install the package from your local checkout:

```sh
git clone https://github.com/alansferreira/curtail-str.git

# Node.js: run from the consuming project
npm install /path/to/curtail-str/packages/node

# Python
python -m pip install /path/to/curtail-str/packages/python

# Go: run inside the consuming module
go mod edit -replace github.com/alansferreira/curtail-str/packages/go=/path/to/curtail-str/packages/go
go get github.com/alansferreira/curtail-str/packages/go

# Java: install io.github.alansferreira:curtail-str:0.1.2 in the local Maven repository
mvn -B -ntp -f /path/to/curtail-str/packages/java/pom.xml install
```

Node.js, Python, and Java have no runtime dependencies. Go uses
`golang.org/x/text` for Unicode normalization.

## Standalone shell package

The [shell package](./packages/shell/README.md) provides independent POSIX
`sh`/`awk`, Windows CMD, and PowerShell scripts. It supports universal mode
without Node.js, Python, Go, or Java. Unicode behavior varies by platform;
see the package guide for restrictions.

```sh
curl -fL https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.sh -o curtail-str.sh
sh curtail-str.sh "active-customer-code-in-the-stock"
# actv-cstm-cd-the-stck
```

Download the complete package:
[TAR.GZ](https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/dist/curtail-str-shell-0.1.2.tar.gz),
[ZIP](https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/dist/curtail-str-shell-0.1.2.zip),
and [SHA-256 checksums](https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/dist/SHA256SUMS).
Replace `main` with a commit SHA or tag to pin an immutable revision.
The package guide includes curl, wget, and Invoke-WebRequest examples.

## Development and verification

The [release guide](./docs/releases.md) documents `make bump`, `make test`,
`make build`, and explicit publication to npm, PyPI, Maven Central, and Go tags.
All packages share the version in [VERSION](./VERSION).

Run from the repository root:

```sh
# Node.js
cd packages/node
npm ci
npm test
npm run typecheck
node test/package-smoke.cjs
cd ../..

# Python: use a virtual environment
python3 -m venv .venv
.venv/bin/python -m pip install -e packages/python build
.venv/bin/python -m unittest discover -s packages/python/tests -v
.venv/bin/python -m build packages/python
.venv/bin/python scripts/check_python_distribution.py packages/python/dist/*.whl packages/python/dist/*.tar.gz

# Go
cd packages/go
go test -race ./...
go vet ./...
cd ../..

# Java
mvn -B -ntp -f packages/java/pom.xml verify

# Shell distribution
python3 scripts/package_shell.py
python3 -m unittest discover -s packages/shell/tests -v
```

All library test runners read the same fixtures, including error cases.
Development tests require the complete checkout; installed packages do not
depend on specification files.

The [CI workflow](./.github/workflows/ci.yml) covers Node.js 22/24/26,
Python 3.11 through 3.15, Go 1.26/1.27, and Temurin 8/11/17/21/25/27.
It also checks installed npm and Python distributions, an external Go
consumer, a standalone JAR consumer, and shell scripts on Linux, macOS,
and Windows.

## Support policy

Use the latest maintenance patch of a supported runtime line. Minimum
requirements are listed above; incompatible requirement changes must be
communicated in an appropriate new package version.

Runtime lifecycle information:
[Node.js](https://github.com/nodejs/Release/blob/main/schedule.json),
[Python](https://devguide.python.org/versions/),
[Go](https://go.dev/doc/devel/release),
and [Eclipse Temurin](https://adoptium.net/support).

## Limitations

- This is a textual heuristic, not a translator or a pronunciation engine.
- Results are not guaranteed to be unique or idempotent. Handle collisions
  before using them as identifiers.
- Unicode classification and case conversion depend on each runtime's Unicode
  database. Characters introduced in different Unicode versions may differ.
- Library APIs reject malformed Unicode rather than silently repairing it.
  Shell scripts have separate, documented Unicode limitations.
- Functions do not mutate arguments. Do not modify replacement maps
  concurrently while a call is running.

## License

Licensed under the [MIT License](./LICENSE).
