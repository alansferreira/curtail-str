import { curtailStr, type Options } from 'curtail-str';

const options: Options = { mode: 'configurable', maxWordLength: 2 };
const result: string = curtailStr('codigo', options);
void result;
// @ts-expect-error Limits require configurable mode.
curtailStr('codigo', { mode: 'custom', maxWordLength: 2 });
