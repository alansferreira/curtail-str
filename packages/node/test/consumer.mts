import { encurtarChaveUniversal, type Options } from '@abbreviate-local/core';

const options: Options = { mode: 'configurable', maxWordLength: 2 };
const result: string = encurtarChaveUniversal('codigo', options);
void result;
// @ts-expect-error Limits require configurable mode.
encurtarChaveUniversal('codigo', { mode: 'custom', maxWordLength: 2 });
