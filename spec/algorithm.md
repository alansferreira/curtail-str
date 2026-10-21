# Contrato do algoritmo

As quatro APIs executam a mesma heuristica, sem traducao, dicionarios ou
garantia de unicidade. Nunca usar a saida como identificador unico sem tratar
colisoes. As funcoes nao modificam parametros nem acessam estado externo.

## Opcoes

| Opcao | Padrao | Significado |
| --- | --- | --- |
| `mode` | `universal` | `universal`, `custom` ou `configurable` |
| `replacements` | ausente | Mapa de palavra para resultado literal |
| `minWordLength` | 3 | Descartar palavras menores |
| `preserveWordLength` | 3 | Preservar palavras restantes ate este tamanho |
| `maxWordLength` | 4 | Limitar apenas palavras comprimidas |

As opcoes numericas sao independentes, inteiras entre 1 e 2147483647.
`replacements` so e aceito em `custom` e `configurable`; limites so em
`configurable`. Opcoes desconhecidas sao erros nas APIs dinamicas.
O mapa vazio e diferente de um mapa ausente para validar o modo.
Nas APIs tipadas Go/Java, mapa `nil`/ausente significa omitido; mapa vazio
nao nulo significa fornecido. Objetos de opcoes ausentes usam os padroes.

Validar todas as opcoes e tipos antes de processar a entrada, mesmo vazia.
Entrada nula retorna `""` (em Go, usar string vazia). Outros tipos invalidos
geram erros. Strings devem conter valores escalares Unicode validos:
rejeitar surrogates isolados e, em Go, UTF-8 invalido, inclusive no mapa.

## Normalizacao e separacao

Converter cada ponto de codigo para minusculas Unicode, isoladamente e sem
localidade; isso evita sigma final contextual. U+0130 vira `i` seguido de
U+0307. Normalizar em NFC apos a conversao. Essa regra tambem vale para chaves
do mapa; valores do mapa sao literais, nao normalizados.

Separar por `-`, `_` e a propriedade Unicode White_Space, fixada como:
U+0009..000D, U+0020, U+0085, U+00A0, U+1680, U+2000..200A,
U+2028, U+2029, U+202F, U+205F, U+3000. Ignorar termos vazios.
Nao separar por outras pontuacoes, digitos, simbolos ou U+FEFF.

Cada chave do mapa deve ser uma palavra nao vazia, sem separadores, mesmo
nas extremidades. Rejeitar colisoes entre chaves normalizadas. Valores devem
ser strings; `""` remove o termo. Uma entrada no mapa prevalece sobre o filtro
de tamanho, preservacao, compressao e truncamento. Valores podem ter caixa
alta, separadores e mais de quatro caracteres: o consumidor os controla.

## Processamento de cada palavra

1. Consultar mapa quando permitido; se houver entrada, usar seu valor final.
2. Contar pontos de codigo NFC. Descartar se menor que `minWordLength`.
3. Preservar se menor ou igual a `preserveWordLength`.
4. Nos demais termos, separar o primeiro ponto de codigo NFC e preserva-lo.
5. Decompor somente o restante em NFD; remover `a/e/i/o/u` e as marcas
   combinantes que os acompanham. Nao remover marcas de consoantes. Recompor
   o restante em NFC e recolocar o primeiro ponto de codigo.
6. Reduzir letras identicas consecutivas a uma, considerando categorias
   Unicode `L*`. Nao colapsar numeros, marcas isoladas ou pontuacao.
7. Cortar o resultado em `maxWordLength` pontos de codigo.
8. Unir resultados nao vazios com `-`.

Preservacao e substituicao nao passam pelo corte. Portanto, os limites nao
precisam ser ordenados. Nao contar bytes, unidades UTF-16 ou grafemas.

## Exemplos

- Universal: `codigo-do-cliente-ativo-no-estoque` -> `cdg-clnt-atv-estq`.
- Universal: `active-customer-code-in-the-stock` -> `actv-cstm-cd-the-stck`.
- Custom com `{"the":"","code":"cdg"}`: o segundo exemplo vira
  `actv-cstm-cdg-stck`.

[cases.json](./cases.json) e o corpus compartilhado pelos quatro runners.
`error: true` exige erro explicito, nao uma string de sucesso.
Casos exclusivos do sistema de tipos de cada linguagem ficam em testes locais.
Os bancos Unicode dos runtimes podem diferir para caracteres adicionados em
versoes recentes; nao se promete equivalencia irrestrita entre bancos distintos.
