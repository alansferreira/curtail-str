import { abbrev } from 'abbrev';

const result: string = abbrev(null);
void result;
// @ts-expect-error Replacement values must be strings.
abbrev('codigo', { mode: 'custom', replacements: { codigo: 1 } });
