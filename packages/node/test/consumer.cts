import { abrev } from 'abrev';

const result: string = abrev(null);
void result;
// @ts-expect-error Replacement values must be strings.
abrev('codigo', { mode: 'custom', replacements: { codigo: 1 } });
