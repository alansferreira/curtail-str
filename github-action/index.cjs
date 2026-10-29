'use strict';

const { appendFileSync } = require('node:fs');
const { randomUUID } = require('node:crypto');
const { curtailStr } = require('../packages/node/index.cjs');

function evaluate(env) {
  const input = name => env[`INPUT_${name.toUpperCase()}`] ?? '';
  const text = input('text');
  const texts = input('texts');
  const format = input('texts-format').trim() || 'auto';
  if (!['auto', 'json', 'lines'].includes(format)) {
    throw new RangeError('texts-format must be auto, json, or lines');
  }
  if (text !== '' && texts !== '') {
    throw new RangeError('text and texts are mutually exclusive');
  }

  const options = { mode: input('mode').trim() || 'universal' };
  if (input('replacements') !== '') {
    options.replacements = JSON.parse(input('replacements'));
  }
  for (const [name, key] of [
    ['min-word-length', 'minWordLength'],
    ['preserve-word-length', 'preserveWordLength'],
    ['max-word-length', 'maxWordLength'],
  ]) {
    const raw = input(name);
    if (raw !== '') {
      if (!/^[0-9]+$/.test(raw.trim())) {
        throw new RangeError(`${name} must be an integer between 1 and 2147483647`);
      }
      options[key] = Number(raw.trim());
    }
  }

  if (texts === '') return { result: curtailStr(text, options) };

  let values;
  if (format === 'json' || (format === 'auto' && texts.trimStart().startsWith('['))) {
    values = JSON.parse(texts);
    if (!Array.isArray(values) || values.some(value => typeof value !== 'string')) {
      throw new TypeError('texts must be a JSON array of strings');
    }
  } else {
    values = texts.split(/\r\n|\n|\r/);
    if (values.at(-1) === '') values.pop();
  }
  curtailStr('', options);
  return { results: JSON.stringify(values.map(value => curtailStr(value, options))) };
}

function run(env) {
  const outputs = evaluate(env);
  if (!env.GITHUB_OUTPUT) throw new Error('GITHUB_OUTPUT is required');
  const commands = Object.entries(outputs).map(([name, value]) => {
    let delimiter;
    do {
      delimiter = `curtail_str_${randomUUID()}`;
    } while (value.includes(delimiter));
    return `${name}<<${delimiter}\n${value}\n${delimiter}\n`;
  }).join('');
  appendFileSync(env.GITHUB_OUTPUT, commands, 'utf8');
}

if (require.main === module) {
  try {
    run(process.env);
  } catch (error) {
    const message = error.message.replaceAll('%', '%25')
      .replaceAll('\r', '%0D').replaceAll('\n', '%0A');
    console.error(`::error::${message}`);
    process.exitCode = 1;
  }
}

module.exports = { evaluate, run };
