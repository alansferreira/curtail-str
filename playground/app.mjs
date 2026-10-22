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
    const output = curtailStr(input.value, options);
    result.textContent = output || '(empty result)';
    const before = Array.from(input.value).length;
    const after = Array.from(output).length;
    stats.textContent = `${before} input / ${after} output code points`;
    snippet.textContent = 'import { curtailStr } from "curtail-str";\n\n' +
      `curtailStr(${JSON.stringify(input.value)}, ${JSON.stringify(options, null, 2)});`;
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
