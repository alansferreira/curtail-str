'use strict';

const separators = /[-_\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+/u;
const letter = /^\p{L}$/u;
const mark = /^\p{M}$/u;
const allowedOptions = new Set([
  'mode', 'replacements', 'minWordLength', 'preserveWordLength', 'maxWordLength',
]);

function validString(value) {
  if (typeof value !== 'string' || !value.isWellFormed()) {
    throw new TypeError('Expected a well-formed Unicode string');
  }
}

function record(value) {
  if (value === null || typeof value !== 'object' ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(value))) {
    throw new TypeError('Expected a plain object');
  }
}

function normalize(value) {
  return Array.from(value, char => char.toLowerCase()).join('').normalize('NFC');
}

function compress(word, maximum) {
  const [first, ...rest] = Array.from(word);
  let tail = '';
  let removing = false;
  for (const char of rest.join('').normalize('NFD')) {
    if ('aeiou'.includes(char)) {
      removing = true;
    } else if (!(removing && mark.test(char))) {
      tail += char;
      removing = false;
    }
  }
  const result = [];
  let previous;
  for (const char of first + tail.normalize('NFC')) {
    if (char !== previous || !letter.test(char)) result.push(char);
    previous = char;
  }
  return result.slice(0, maximum).join('');
}

function encurtarChaveUniversal(input, options = {}) {
  record(options);
  for (const key of Reflect.ownKeys(options)) {
    if (!allowedOptions.has(key)) throw new TypeError(`Unknown option: ${String(key)}`);
  }
  const own = key => Object.hasOwn(options, key);
  const mode = own('mode') ? options.mode : 'universal';
  if (!['universal', 'custom', 'configurable'].includes(mode)) {
    throw new RangeError('Unknown mode');
  }
  if (own('replacements') && mode === 'universal') {
    throw new RangeError('Replacements require custom or configurable mode');
  }
  const limits = {};
  for (const [key, fallback] of [
    ['minWordLength', 3], ['preserveWordLength', 3], ['maxWordLength', 4],
  ]) {
    if (own(key) && mode !== 'configurable') {
      throw new RangeError('Limits require configurable mode');
    }
    const value = own(key) ? options[key] : fallback;
    if (!Number.isInteger(value) || value < 1 || value > 2147483647) {
      throw new RangeError(`${key} must be an integer between 1 and 2147483647`);
    }
    limits[key] = value;
  }
  const replacements = new Map();
  if (own('replacements')) {
    record(options.replacements);
    for (const key of Reflect.ownKeys(options.replacements)) {
      validString(key);
      const value = options.replacements[key];
      validString(value);
      const normalized = normalize(key);
      if (!normalized || separators.test(normalized) || replacements.has(normalized)) {
        throw new RangeError('Invalid or colliding replacement key');
      }
      replacements.set(normalized, value);
    }
  }
  if (input === null || input === undefined) return '';
  validString(input);
  const output = [];
  for (const word of normalize(input).split(separators)) {
    if (!word) continue;
    let result;
    if (replacements.has(word)) {
      result = replacements.get(word);
    } else {
      const length = Array.from(word).length;
      if (length < limits.minWordLength) continue;
      result = length <= limits.preserveWordLength
        ? word : compress(word, limits.maxWordLength);
    }
    if (result) output.push(result);
  }
  return output.join('-');
}

module.exports = { encurtarChaveUniversal };
