# curtail-str for Python

Requires Python 3.11 or later. No runtime dependencies. Includes type
annotations and a `py.typed` marker.

## Install from source

```sh
python -m pip install /path/to/curtail-str/packages/python
```

The distribution name is `curtail-str`; the import name is `curtail_str`.

## Usage

```python
from curtail_str import curtail_str

assert curtail_str("active-customer-code-in-the-stock") == "actv-cstm-cd-the-stck"
assert curtail_str("code-in-the-stock", {
    "mode": "custom",
    "replacements": {"the": "", "code": "cdg"},
}) == "cdg-stck"
assert curtail_str("customer", {
    "mode": "configurable", "max_word_length": 2,
}) == "cs"
```

`None` returns `""`. Omitted options or `None` use defaults. Invalid arguments
raise `TypeError` or `ValueError`, even for empty input. Replacement maps
associate strings with literal results; `""` removes a word.

The default `universal` mode does not accept a replacement map.
The positive integer limits `min_word_length` (3), `preserve_word_length` (3),
and `max_word_length` (4) are independent and available only in `configurable`.
Preserved words and replacement values are not truncated. Arguments are not
mutated.

The heuristic does not translate words or guarantee uniqueness. It counts
Unicode code points and preserves the first code point of compressed words.
By default, `code` becomes `cd` and `the` remains `the`.

## Development

Install with `python -m pip install -e .` and run
`python -m unittest discover -s tests -v` from this directory.
Contract tests require the fixtures at the repository root; the installed
package does not depend on them.

See the [algorithm contract](../../spec/algorithm.md) for complete semantics.
