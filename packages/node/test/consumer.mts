import { abrev, type Options } from 'abrev';

const options: Options = { mode: 'configurable', maxWordLength: 2 };
const result: string = abrev('codigo', options);
void result;
// @ts-expect-error Limits require configurable mode.
abrev('codigo', { mode: 'custom', maxWordLength: 2 });
