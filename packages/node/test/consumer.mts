import { abbrev, type Options } from 'abbrev';

const options: Options = { mode: 'configurable', maxWordLength: 2 };
const result: string = abbrev('codigo', options);
void result;
// @ts-expect-error Limits require configurable mode.
abbrev('codigo', { mode: 'custom', maxWordLength: 2 });
