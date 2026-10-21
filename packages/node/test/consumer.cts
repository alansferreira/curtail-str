import { curtailStr } from 'curtail-str';

const result: string = curtailStr(null);
void result;
// @ts-expect-error Replacement values must be strings.
curtailStr('codigo', { mode: 'custom', replacements: { codigo: 1 } });
