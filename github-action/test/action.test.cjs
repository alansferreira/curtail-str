'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, readFileSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { evaluate, run } = require('../index.cjs');
const cases = require('../../spec/cases.json');

function inputs(values) {
  return Object.fromEntries(Object.entries(values)
    .map(([key, value]) => [`INPUT_${key.toUpperCase()}`, value]));
}

test('action metadata resolves its entry point relative to the action folder', () => {
  const actionDirectory = path.join(__dirname, '..');
  const metadata = readFileSync(path.join(actionDirectory, 'action.yml'), 'utf8');
  const main = metadata.match(/^  main: (.+)$/m);
  assert.ok(main, 'Action must declare an entry point');
  assert.equal(require(path.join(actionDirectory, main[1])).run, run);
});

for (const item of cases) {
  test(`action contract: ${item.name}`, () => {
    const env = inputs({ text: item.input ?? '' });
    const names = {
      mode: 'mode',
      replacements: 'replacements',
      minWordLength: 'min-word-length',
      preserveWordLength: 'preserve-word-length',
      maxWordLength: 'max-word-length',
    };
    for (const [key, value] of Object.entries(item.options ?? {})) {
      Object.assign(env, inputs({
        [names[key]]: key === 'replacements' ? JSON.stringify(value) : String(value),
      }));
    }
    if (item.error) assert.throws(() => evaluate(env));
    else assert.deepEqual(evaluate(env), { result: item.expected });
  });
}

test('batch JSON and lines preserve order, duplicates, and empty results', () => {
  const values = ['customer', '', 'code', 'in', 'customer', 'Árvore'];
  const expected = { results: '["cstm","","cd","","cstm","árvr"]' };
  assert.deepEqual(evaluate(inputs({ texts: JSON.stringify(values) })), expected);
  for (const separator of ['\n', '\r\n', '\r']) {
    for (const suffix of ['', separator]) {
      assert.deepEqual(evaluate(inputs({
        texts: values.join(separator) + suffix,
      })), expected);
    }
  }
});

test('batch format can be explicit and JSON preserves embedded newlines', () => {
  assert.deepEqual(evaluate(inputs({ texts: '  ["customer\\ncode", ""]  ' })), {
    results: '["cstm-cd",""]',
  });
  assert.deepEqual(evaluate(inputs({ texts: '[]', 'texts-format': 'json' })), {
    results: '[]',
  });
  assert.deepEqual(evaluate(inputs({ texts: '[customer', 'texts-format': 'lines' })), {
    results: '["[cst"]',
  });
  assert.deepEqual(evaluate(inputs({ texts: 'customer\n\n' })), {
    results: '["cstm",""]',
  });
  assert.deepEqual(evaluate(inputs({ texts: '\n' })), { results: '[""]' });
});

test('all batch items use the same custom and configurable options', () => {
  assert.deepEqual(evaluate(inputs({
    texts: '["customer-code", "code", "customer-code"]',
    mode: 'custom',
    replacements: '{"code":"cdg"}',
  })), { results: '["cstm-cdg","cdg","cstm-cdg"]' });
  assert.deepEqual(evaluate(inputs({
    texts: 'customer\ncode',
    mode: 'configurable',
    'min-word-length': '1',
    'preserve-word-length': '1',
    'max-word-length': '2',
  })), { results: '["cs","cd"]' });
});

test('invalid inputs fail, including options on empty batches', () => {
  for (const values of [
    { text: 'customer', texts: '["code"]' },
    { texts: '[broken' },
    { texts: '["customer", null]' },
    { texts: '["customer", 42]' },
    { texts: '["customer", {}]' },
    { texts: '["\\ud800"]' },
    { texts: '{}', 'texts-format': 'json' },
    { texts: 'null', 'texts-format': 'json' },
    { texts: '"customer"', 'texts-format': 'json' },
    { texts: 'customer', 'texts-format': 'json' },
    { texts: 'customer', 'texts-format': 'yaml' },
    { replacements: '{broken' },
    { mode: 'custom', replacements: '[]' },
    { mode: 'custom', replacements: '{"code":null}' },
    { texts: '[]', mode: 'unknown' },
    { texts: '[]', replacements: '{}' },
    { texts: '[]', 'max-word-length': '2' },
    ...['1.5', '1e2', '0x10', 'NaN', 'Infinity', '-1', ' ', '2147483648', '0']
      .map(value => ({ mode: 'configurable', 'max-word-length': value })),
  ]) assert.throws(() => evaluate(inputs(values)), JSON.stringify(values));
});

test('empty single input is valid and whitespace is not trimmed', () => {
  assert.deepEqual(evaluate({}), { result: '' });
  assert.deepEqual(evaluate(inputs({
    text: '\ufeffcustomer',
    mode: 'custom',
    replacements: '{"\\ufeffcustomer":"  literal  "}',
  })), { result: '  literal  ' });
});

test('entry point writes exact multiline outputs independently of working directory', t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'curtail-str-action-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const output = path.join(directory, 'output');
  const env = Object.fromEntries(Object.entries(process.env)
    .filter(([name]) => !name.startsWith('INPUT_')));
  Object.assign(env, inputs({
    text: 'customer',
    mode: 'custom',
    replacements: '{"customer":" A\\n::warning::literal\\r\\nB% "}',
  }), { GITHUB_OUTPUT: output });
  const child = spawnSync(process.execPath, [path.join(__dirname, '../index.cjs')], {
    env, cwd: directory, encoding: 'utf8',
  });
  assert.equal(child.status, 0, child.stderr);
  assert.equal(child.stdout, '');
  const content = readFileSync(output, 'utf8');
  const delimiter = content.split('\n')[0].slice('result<<'.length);
  assert.equal(content, `result<<${delimiter}\n A\n::warning::literal\r\nB% \n${delimiter}\n`);

  writeFileSync(output, '');
  run({ ...inputs({ texts: 'customer\ncode\n' }), GITHUB_OUTPUT: output });
  const batchOutput = readFileSync(output, 'utf8');
  assert.match(batchOutput, /^results<<([^\n]+)\n\["cstm","cd"\]\n\1\n$/);

  const failed = spawnSync(process.execPath, [path.join(__dirname, '../index.cjs')], {
    env: { ...env, ...inputs({ texts: '["code"]' }) }, encoding: 'utf8',
  });
  assert.equal(failed.status, 1);
  assert.match(failed.stderr, /::error::text and texts are mutually exclusive/);
  assert.equal(readFileSync(output, 'utf8'), batchOutput);
});

test('output failures are explicit and batches are atomic', t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'curtail-str-action-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const output = path.join(directory, 'output');
  assert.throws(() => run(inputs({ text: 'customer' })), /GITHUB_OUTPUT/);
  assert.throws(() => run({ GITHUB_OUTPUT: directory }), /EISDIR|EPERM|EACCES/);
  assert.throws(() => run({
    ...inputs({ texts: '["customer","\\ud800"]' }), GITHUB_OUTPUT: output,
  }));
  assert.throws(() => readFileSync(output), /ENOENT/);
});
