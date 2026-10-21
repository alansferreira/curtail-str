# Abbreviate

Microbibliotecas puras para abreviar identificadores em Node.js, Python, Go e
Java. Mesmas regras, tres modos explicitos, sem dicionarios de idiomas.

```text
codigo-do-cliente-ativo-no-estoque -> cdg-clnt-atv-estq
active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
```

O segundo exemplo segue as regras: `code` vira `cd` e termos com tres letras,
como `the`, sao preservados. Para obter `actv-cstm-cdg-stck`, fornecer o mapa
`{"the": "", "code": "cdg"}` no modo personalizado.

## Modos

| Modo | Comportamento |
| --- | --- |
| `universal` | Padrao: descartar termos menores que 3, preservar termos de 3, comprimir os demais e limitar a 4 |
| `custom` | Aplicar mapa opcional antes das regras universais |
| `configurable` | Aplicar mapa opcional e permitir tres limites independentes |

Na compressao, preservar o primeiro ponto de codigo, remover as vogais do
restante (incluindo acentos), colapsar letras identicas consecutivas e truncar.
Separadores: hifen ASCII, underscore e espacos Unicode. Normalizacao NFC e
minusculas independentes da localidade; comprimentos usam pontos de codigo.
Outras pontuacoes, numeros e simbolos nao sao removidos.

Os valores do mapa sao resultados **literais**: nao sao normalizados,
comprimidos ou truncados. String vazia remove uma palavra. Chaves passam pela
mesma normalizacao da entrada; chaves vazias, com separadores ou que colidam
depois da normalizacao geram erro.

Limites so sao permitidos em `configurable`; mapa nao e permitido em
`universal`, mesmo vazio. Palavras preservadas e substituicoes nao passam
pelo limite de compressao. Limites aceitam inteiros em 1..2147483647, sem
exigir ordenacao entre eles. Entradas nulas/vazias retornam string vazia
quando as opcoes sao validas; opcoes invalidas sempre geram erro explicito.
Em Go, `string` nao admite `nil`; usar `""`.

Consulte o [contrato normativo](./spec/algorithm.md) e os
[vetores de teste](./spec/cases.json).

## Pacotes e compatibilidade

| Linguagem | Minimo | API e instrucoes |
| --- | --- | --- |
| Node.js | 22 | [abbreviate](./packages/node/README.md), ESM/CommonJS e tipos TypeScript |
| Python | 3.11 | [abbreviate](./packages/python/README.md), pacote tipado |
| Go | 1.26 | [Abbreviate](./packages/go/README.md), retorno `(string, error)` |
| Java | 8, Eclipse Temurin | [Abbreviate.abbreviate](./packages/java/README.md), JAR sem dependencias de runtime |

| Opcao | Node.js / Java | Python | Go | Padrao |
| --- | --- | --- | --- | --- |
| Modo | `mode` | `mode` | `Mode` | universal |
| Mapa | `replacements` | `replacements` | `Replacements` | ausente |
| Minimo | `minWordLength` | `min_word_length` | `MinWordLength` | 3 |
| Preservacao | `preserveWordLength` | `preserve_word_length` | `PreserveWordLength` | 3 |
| Corte | `maxWordLength` | `max_word_length` | `MaxWordLength` | 4 |

Java usa enum `Mode` e builder imutavel; Go usa constantes tipadas e ponteiros
opcionais nos limites. Consulte os exemplos por pacote.

### Instalacao local

Os nomes abaixo sao locais/provisorios; nenhum pacote foi publicado.

```sh
# Node.js, a partir de um projeto consumidor
npm install /caminho/abbreviate/packages/node

# Python
python -m pip install /caminho/abbreviate/packages/python

# Go, dentro do modulo consumidor
go mod edit -replace github.com/alansferreira/abbreviate/packages/go=/caminho/abbreviate/packages/go
go get github.com/alansferreira/abbreviate/packages/go

# Java: instalar coordenadas local.abbreviate:abbreviate:0.1.0 no Maven local
mvn -B -ntp -f /caminho/abbreviate/packages/java/pom.xml install
```

Node.js, Python e Java nao possuem dependencias de runtime. Go utiliza
`golang.org/x/text` para normalizacao Unicode.

## Testes e distribuicao

Executar a partir da raiz do monorepositorio:

```sh
# Node.js
cd packages/node
npm ci
npm test
npm run typecheck
node test/package-smoke.cjs
cd ../..

# Python: usar ambiente virtual
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
```

Todos os runners leem o mesmo corpus, incluindo casos de erro. Os testes de
desenvolvimento precisam do monorepositorio completo; nenhum consumidor
depende dos arquivos de especificacao.

A [CI](./.github/workflows/ci.yml) cobre as linhas Node 22/24/26, Python
3.11..3.15, Go 1.26/1.27 e Temurin 8/11/17/21/25/27, usando patches recentes.
Tambem instala o tarball npm, wheel e sdist Python, consome o modulo Go fora
da raiz e compila um consumidor Java apenas com o JAR gerado.

## Politica de suporte

Minimos escolhidos em 21/10/2026: a linha oficialmente mantida mais antiga de
cada linguagem; para Java, a LTS mais antiga mantida pelo Eclipse Temurin.
Node 20 e Python 3.10 ja encerraram suporte. Go mantem as duas linhas mais
recentes. Usar sempre o patch mais recente da linha escolhida.

Fontes oficiais:
[Node.js](https://github.com/nodejs/Release/blob/main/schedule.json),
[Python](https://devguide.python.org/versions/),
[Go](https://go.dev/doc/devel/release),
[Temurin](https://adoptium.net/support).

Revisar a matriz quando as linhas encerrarem suporte. Nao elevar os minimos
de uma versao publicada silenciosamente; comunicar alteracoes incompativeis
em uma nova versao apropriada.

## Limites e escopo

- A heuristica nao traduz, nao garante pronuncia, unicidade ou idempotencia.
- Abreviar pode causar colisoes; nao substituir validacao de identificadores.
- Letras e caixa Unicode dependem do banco do runtime. Os casos contratados
  sao testados, mas caracteres de versoes Unicode diferentes podem divergir.
- Strings Unicode malformadas sao rejeitadas, nao reparadas silenciosamente.
- Nenhum parametro e alterado; consumidores nao devem modificar mapas
  concorrentemente durante chamadas.
- Publicacao, licenca de distribuicao, nomes definitivos de registro, CLI,
  traducoes e integracao Git ficam para uma etapa posterior.
