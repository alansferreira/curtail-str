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
  const minEsm = await import('curtail-str/curtail-str.min.mjs');
  const minUmd = require('../dist/curtail-str.min.js');
  assert.equal(esm.curtailStr('codigo'), 'cdg');
  assert.equal(minEsm.curtailStr('codigo-do-cliente'), 'cdg-clnt');
  assert.equal(minUmd.curtailStr('codigo-do-cliente'), 'cdg-clnt');
  assert.equal(shorten(undefined), '');
});

test('UMD browser global and AMD exports', () => {
  const fs = require('node:fs');
  const path = require('node:path');
  const vm = require('node:vm');
  const code = fs.readFileSync(path.join(__dirname, '../dist/curtail-str.min.js'), 'utf8');

  const browserContext = vm.createContext({});
  vm.runInContext(code, browserContext);
  assert.equal(browserContext.curtailStr.curtailStr('codigo-do-cliente'), 'cdg-clnt');

  let amdExport;
  const define = (deps, factory) => {
    amdExport = factory();
  };
  define.amd = true;
  const amdContext = vm.createContext({ define });
  vm.runInContext(code, amdContext);
  assert.equal(amdExport.curtailStr('codigo-do-cliente'), 'cdg-clnt');
});

test('prototype-like keys are ordinary entries', () => {
  const replacements = JSON.parse('{"__proto__":"invalid"}');
  assert.throws(() => shorten('', { mode: 'custom', replacements }));
  assert.equal(shorten('constructor', {
    mode: 'custom', replacements: { constructor: 'OK' },
  }), 'OK');
});
