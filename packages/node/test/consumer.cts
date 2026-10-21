import { encurtarChaveUniversal } from '@abbreviate-local/core';

const result: string = encurtarChaveUniversal(null);
void result;
// @ts-expect-error Replacement values must be strings.
encurtarChaveUniversal('codigo', { mode: 'custom', replacements: { codigo: 1 } });
