import { curtailStr } from 'curtail-str';

let sampleInput = 'active-customer-code-in-the-stock';
const universal = curtailStr(sampleInput);
console.log(`Universal: ${sampleInput} -> ${universal}`);

sampleInput = 'customer-code';
const custom = curtailStr(sampleInput, {
  mode: 'custom',
  replacements: { code: 'cdg' },
});
console.log(`Custom: ${sampleInput} -> ${custom}`);

sampleInput = 'customer';
const configurable = curtailStr(sampleInput, {
  mode: 'configurable',
  maxWordLength: 2,
});
console.log(`Configurable: ${sampleInput} -> ${configurable}`);
