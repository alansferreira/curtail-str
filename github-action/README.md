# GitHub Action

The reusable [action](./action.yml) shortens identifiers using the existing
[Node.js implementation](../packages/node/index.cjs). It supports all three
[algorithm modes](../spec/algorithm.md) on Linux, macOS, and Windows.
It uses the GitHub runner's Node.js 24 runtime: consumers do not need
`actions/setup-node`, `npm install`, or a checkout of their own repository.
No packages are downloaded during execution.

## Structure

```text
github-action/
  action.yml                  # Public action metadata
  index.cjs                   # Input parsing and output handling
  test/action.test.cjs         # Contract and integration tests
  README.md                   # Usage and development guide
.github/workflows/ci-action.yml # Dedicated action CI
```

All action-specific files live in `github-action/`. The adapter imports the
Node.js library from `packages/node/index.cjs`, keeping the algorithm in one
place. Consumers use `alansferreira/curtail-str/github-action@<ref>`.

## Single value

```yaml
steps:
  - name: Shorten identifier
    id: shorten
    uses: alansferreira/curtail-str/github-action@main
    with:
      text: active-customer-code-in-the-stock
  - name: Use result
    env:
      RESULT: ${{ steps.shorten.outputs.result }}
    run: printf '%s\n' "$RESULT"
    shell: bash
```

Output: `actv-cstm-cd-the-stck`.

These examples use `main`, which becomes available after the action is merged
and pushed. For production, pin a full commit SHA containing the action.
Future repository release tags (`vX.Y.Z`) can also select the action; tags
created before the action was added do not contain it.
Self-hosted runners must support JavaScript actions using Node.js 24
(runner version 2.327.1 or later).

## Multiple values: JSON first

```yaml
- name: Shorten JSON array
  id: batch
  uses: alansferreira/curtail-str/github-action@main
  with:
    texts: '["customer-code", "code", "in", "customer-code"]'
    mode: custom
    replacements: '{"code":"cdg"}'
```

`steps.batch.outputs.results` is the JSON string
`["cstm-cdg","cdg","","cstm-cdg"]`. Order, duplicate entries, and empty
results are preserved. The same options apply to every entry. Use
`${{ fromJSON(steps.batch.outputs.results) }}` in expressions that need an array.

Line-separated input is also supported:

```yaml
- name: Shorten lines
  id: batch
  uses: alansferreira/curtail-str/github-action@main
  with:
    texts: |
      customer
      code
      in
    mode: configurable
    min-word-length: '1'
    preserve-word-length: '1'
    max-word-length: '2'
```

`steps.batch.outputs.results` is `["cs","cd","in"]`.

### Format rules

- `texts-format: auto` (default): if the first non-whitespace character is `[`,
  parse as JSON; otherwise split into lines. Malformed JSON arrays fail rather
  than falling back to lines.
- `texts-format: json`: always require a JSON array containing only strings.
  `[]` returns `[]`. Nulls, numbers, objects, and nested arrays are rejected.
- `texts-format: lines`: always split into lines, even for values beginning
  with `[`. CRLF, LF, and CR separators are accepted. Exactly one terminal
  line break is ignored to support YAML's `|` syntax. Other empty lines are
  retained as empty entries. Values are not trimmed.
- Use JSON when an individual value contains a line break or when an empty
  final entry must be unambiguous. For example, `["customer", ""]`.

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `text` | empty string | Single value; mutually exclusive with non-empty `texts` |
| `texts` | omitted | JSON array or line-separated values |
| `texts-format` | `auto` | `auto`, `json`, or `lines` |
| `mode` | `universal` | `universal`, `custom`, or `configurable` |
| `replacements` | omitted | JSON object with string values; only in `custom` or `configurable` |
| `min-word-length` | `3` | Discard shorter words; only in `configurable` |
| `preserve-word-length` | `3` | Preserve remaining words up to this length; only in `configurable` |
| `max-word-length` | `4` | Limit compressed words; only in `configurable` |

Length limits must be decimal integers from 1 through 2147483647. Replacements
are literal strings; an empty replacement removes a word. Explicitly supplying
`{}` still counts as a replacement map, so it is invalid in `universal` mode.
Supplying length limits in other modes is also an error, even if they match
the defaults.

GitHub represents both omitted and explicitly empty inputs as empty strings.
An empty `texts` therefore selects single-value mode; use `texts: '[]'` for an
empty batch and `texts: '[""]'` for a batch containing one empty string.
With neither input supplied, `result` is an empty string.

## Outputs and failures

| Output | Available when | Shape |
| --- | --- | --- |
| `result` | Single-value mode | Abbreviated string |
| `results` | Batch mode | JSON array string, including empty results in their original positions |

Invalid input or options fail the step with an error annotation and a nonzero
exit code. Options are validated even for an empty batch. A failed batch writes
no outputs; it never returns partial results or skips invalid entries.

Outputs use GitHub's output file protocol, including multiline literal
replacements. When passing results to shell commands, use environment
variables as in the single-value example instead of interpolating output
expressions directly into shell code.

## Verification

From the repository root with Node.js 24:

```sh
make test-action
# Or, without Make:
node --test github-action/test/action.test.cjs

# Or, from github-action/:
node --test test/action.test.cjs
```

The tests cover the shared algorithm fixtures, both batch formats, ordered
results, validation, and output handling. The
[CI workflow](../.github/workflows/ci-action.yml) also runs the actual local action
with single, JSON, and line-separated inputs on all three operating systems.
