import { abbreviate, type Options } from 'abbreviate';

const options: Options = { mode: 'configurable', maxWordLength: 2 };
const result: string = abbreviate('codigo', options);
void result;
// @ts-expect-error Limits require configurable mode.
abbreviate('codigo', { mode: 'custom', maxWordLength: 2 });
