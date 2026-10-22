import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { curtailStr } from '../../playground/dist/core.mjs';

const cases = JSON.parse(await readFile(new URL('../../spec/cases.json', import.meta.url), 'utf8'));
for (const item of cases) {
  test(`browser core: ${item.name}`, () => {
    if (item.error) {
      assert.throws(() => curtailStr(item.input, item.options));
    } else {
      assert.equal(curtailStr(item.input, item.options), item.expected);
    }
  });
}

test('browser build contains no CommonJS or remote dependencies', async () => {
  const core = await readFile(new URL('../../playground/dist/core.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(core, /module\.exports|require\(/);
  const app = await readFile(new URL('../../playground/dist/app.mjs', import.meta.url), 'utf8');
  assert.match(app, /import \{ curtailStr \} from '\.\/core\.mjs'/);
  assert.doesNotMatch(app, /innerHTML|fetch\(|https?:\/\//);
});
