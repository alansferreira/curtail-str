# Algorithm contract

The four library APIs implement the same dictionary-free heuristic without
translation or uniqueness guarantees. Handle collisions before using results
as unique identifiers. Functions do not mutate arguments or access external
state. Shell scripts have a separate contract in their [guide](../packages/shell/README.md).

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `mode` | `universal` | `universal`, `custom`, or `configurable` |
| `replacements` | omitted | Map from a word to a literal result |
| `minWordLength` | 3 | Discard shorter words |
| `preserveWordLength` | 3 | Preserve remaining words up to this length |
| `maxWordLength` | 4 | Limit compressed words only |

Numeric options are independent integers from 1 through 2147483647.
`replacements` is accepted only in `custom` and `configurable`; length options
are accepted only in `configurable`. Dynamic APIs reject unknown options.
For mode validation, an empty map is different from an omitted map.
In Go and Java, a nil or absent map means omitted; a non-null empty map counts
as supplied. Omitted options use defaults.

Validate all options and types before processing input, including empty input.
Null input returns `""` (use an empty string in Go). Other invalid input types
produce errors. Strings must contain valid Unicode scalar values: reject
unpaired surrogates and, in Go, invalid UTF-8, including replacement keys and
values.

## Normalization and splitting

Lowercase each Unicode code point individually, without locale-dependent rules.
This avoids contextual final sigma. U+0130 becomes `i` followed by U+0307.
Normalize to NFC after lowercasing. Apply this normalization to replacement
keys as well; replacement values remain literal.

Split on `-`, `_`, and the following fixed Unicode White_Space set:
U+0009..000D, U+0020, U+0085, U+00A0, U+1680, U+2000..200A,
U+2028, U+2029, U+202F, U+205F, U+3000. Ignore empty terms.
Do not split on other punctuation, digits, symbols, or U+FEFF.

Each replacement key must be a non-empty word without separators, including
leading or trailing separators. Reject normalized key collisions. Values must
be strings; `""` removes a term. A replacement takes precedence over length
filtering, preservation, compression, and truncation. Values may contain
uppercase letters, separators, and more than four characters.

## Word processing

1. Look up the word in the replacement map when allowed. If present, use the
   replacement as the final result.
2. Count NFC code points. Discard words shorter than `minWordLength`.
3. Preserve words whose length is at most `preserveWordLength`.
4. For other words, separate and preserve the first NFC code point.
5. Decompose only the remainder to NFD. Remove `a/e/i/o/u` and their following
   combining marks. Preserve marks attached to consonants. Recompose the
   remainder to NFC and restore the first code point.
6. Collapse consecutive identical letters, using Unicode categories `L*`.
   Do not collapse digits, isolated combining marks, or punctuation.
7. Truncate the result to `maxWordLength` code points.
8. Join non-empty results with `-`.

Preserved words and replacements bypass truncation, so length limits do not
need to be ordered. Count code points, not bytes, UTF-16 units, or graphemes.

## Examples

- Universal: `active-customer-code-in-the-stock` -> `actv-cstm-cd-the-stck`.
- Universal: `codigo-do-cliente-ativo-no-estoque` -> `cdg-clnt-atv-estq`.
- Custom with `{"the":"","code":"cdg"}`: the first example becomes
  `actv-cstm-cdg-stck`.

[cases.json](./cases.json) contains the fixtures shared by all four runners.
`error: true` requires an explicit error, not a success-shaped string.
Language-specific type-system cases belong in each package's tests.
Runtime Unicode databases may differ for recently introduced characters;
unrestricted equivalence across different databases is not guaranteed.
