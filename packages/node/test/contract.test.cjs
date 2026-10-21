const { test } = require('node:test');
const assert = require('node:assert/strict');
const cases = require('../../../spec/cases.json');
const { curtailStr: shorten } = require('..');

for (const item of cases) {
  test(item.name, () => {
    const snapshot = JSON.stringify(item);
    if (item.error) assert.throws(() => shorten(item.input, item.options));
    else {
      assert.equal(shorten(item.input, item.options), item.expected);
      assert.equal(shorten(item.input, item.options), item.expected);
    }
    assert.equal(JSON.stringify(item), snapshot);
  });
}

test('invalid dynamic types', () => {
  for (const value of [1, [], {}, true, '\ud800']) {
    assert.throws(() => shorten(value), TypeError);
  }
  for (const options of [
    null, [], { extra: 1 }, { mode: undefined },
    { mode: 'configurable', maxWordLength: true },
    { mode: 'configurable', maxWordLength: 1.5 },
    { mode: 'custom', replacements: null },
    { mode: 'custom', replacements: { abc: 1 } },
    { mode: 'custom', replacements: { abc: '\ud800' } },
  ]) assert.throws(() => shorten('', options));
});

test('ESM and CommonJS exports', async () => {
  const esm = await import('curtail-str');
  assert.equal(esm.curtailStr('codigo'), 'cdg');
  assert.equal(shorten(undefined), '');
});

test('prototype-like keys are ordinary entries', () => {
  const replacements = JSON.parse('{"__proto__":"invalid"}');
  assert.throws(() => shorten('', { mode: 'custom', replacements }));
  assert.equal(shorten('constructor', {
    mode: 'custom', replacements: { constructor: 'OK' },
  }), 'OK');
});
