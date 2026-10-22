# curtail-str for Node.js

Requires Node.js 22 or later. No runtime dependencies. Supports ESM, CommonJS,
and TypeScript declarations.

## Install from source

From the consuming project:

```sh
npm install /path/to/curtail-str/packages/node
```

## Usage

```js
import { curtailStr } from 'curtail-str';
// CommonJS: const { curtailStr } = require('curtail-str');

curtailStr('active-customer-code-in-the-stock'); // 'actv-cstm-cd-the-stck'
curtailStr('code-in-the-stock', {
  mode: 'custom',
  replacements: { the: '', code: 'cdg' },
}); // 'cdg-stck'
curtailStr('customer', {
  mode: 'configurable',
  maxWordLength: 2,
}); // 'cs'
```

`null` and `undefined` return `''`. Invalid arguments throw `TypeError` or
`RangeError`, even for empty input. Replacement maps are plain objects with
string values; values are literal results, and `''` removes a word.

The default `universal` mode does not accept a replacement map.
The positive integer limits `minWordLength` (3), `preserveWordLength` (3),
and `maxWordLength` (4) are independent and available only in `configurable`.
Preserved words and replacements are not truncated. Arguments are not mutated.

This heuristic does not translate words or guarantee uniqueness. It counts
Unicode code points, preserves the first code point, and removes vowels from
the rest of compressed words. By default, `code` becomes `cd` and `the` remains
`the`.

## Development

Run `npm ci`, `npm test`, `npm run typecheck`, and
`node test/package-smoke.cjs` from this directory. Contract tests use fixtures
at the repository root; the installed package does not depend on them.

See the [algorithm contract](https://github.com/alansferreira/curtail-str/blob/main/spec/algorithm.md) for complete semantics.
