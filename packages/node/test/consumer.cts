import { abbreviate } from 'abbreviate';

const result: string = abbreviate(null);
void result;
// @ts-expect-error Replacement values must be strings.
abbreviate('codigo', { mode: 'custom', replacements: { codigo: 1 } });
