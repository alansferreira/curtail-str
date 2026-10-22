import { curtailStr } from './core.mjs';

const form = document.querySelector('#playground');
const input = document.querySelector('#input');
const mode = document.querySelector('#mode');
const replacements = document.querySelector('#replacements');
const replacementFields = document.querySelector('#replacement-fields');
const limitFields = document.querySelector('#limit-fields');
const result = document.querySelector('#result');
const stats = document.querySelector('#stats');
const error = document.querySelector('#error');
const snippet = document.querySelector('#snippet');
const descriptions = {
  universal: 'Remove short words, preserve three-character terms, compress longer words.',
  custom: 'Apply replacements before the universal rules. Replacement values bypass compression.',
  configurable: 'Apply replacements and independent length limits. Preserved words bypass truncation.',
};

function update() {
  replacementFields.hidden = replacementFields.disabled = mode.value === 'universal';
  limitFields.hidden = limitFields.disabled = mode.value !== 'configurable';
  document.querySelector('#mode-help').textContent = descriptions[mode.value];
  try {
    const options = { mode: mode.value };
    if (mode.value !== 'universal') {
      options.replacements = JSON.parse(replacements.value);
    }
    if (mode.value === 'configurable') {
      options.minWordLength = document.querySelector('#minimum').valueAsNumber;
      options.preserveWordLength = document.querySelector('#preserve').valueAsNumber;
      options.maxWordLength = document.querySelector('#maximum').valueAsNumber;
    }
    const lines = input.value.split(/\r?\n/).filter(line => line.trim() !== '');
    const outputs = lines.map(line => curtailStr(line, options));
    const output = outputs.join('\n');
    result.textContent = outputs.length ? outputs.map(item => item || '(empty result)').join('\n') : '(empty result)';
    const before = lines.reduce((sum, line) => sum + Array.from(line).length, 0);
    const after = outputs.reduce((sum, item) => sum + Array.from(item).length, 0);
    const lineLabel = lines.length === 1 ? '1 line' : `${lines.length} lines`;
    stats.textContent = `${lineLabel} · ${before} input / ${after} output code points`;
    const callCode = lines.length <= 1
      ? `curtailStr(${JSON.stringify(lines[0] ?? '')}, ${JSON.stringify(options, null, 2)});`
      : `const options = ${JSON.stringify(options, null, 2)};\n` +
        `${JSON.stringify(lines, null, 2)}.map(line => curtailStr(line, options));`;
    snippet.textContent = 'import { curtailStr } from "curtail-str";\n\n' + callCode;
    error.hidden = true;
    error.textContent = '';
  } catch (cause) {
    result.textContent = 'Invalid configuration';
    stats.textContent = '';
    snippet.textContent = '';
    error.textContent = cause.message;
    error.hidden = false;
  }
}

form.addEventListener('input', update);
form.addEventListener('change', update);
form.addEventListener('submit', event => event.preventDefault());
for (const button of form.querySelectorAll('[data-example]')) {
  button.addEventListener('click', () => {
    input.value = button.dataset.example;
    update();
  });
}
update();
