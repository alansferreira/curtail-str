# Abrev para Node.js

Node.js 22 ou superior. Pacote local, sem dependencias de runtime.
Este pacote ainda nao foi publicado: instale pelo caminho local.
Os imports abaixo resolvem o pacote local instalado. O registro npm nao
retornou um pacote `abrev` em 21/10/2026; o nome ainda nao foi reservado.

```js
import { abrev } from 'abrev';
// CommonJS: const { abrev } = require('abrev');

abrev('codigo-do-cliente'); // 'cdg-clnt'
abrev('code-in-the-stock', {
  mode: 'custom',
  replacements: { the: '', code: 'cdg' },
}); // 'cdg-stck'
abrev('cliente', {
  mode: 'configurable',
  maxWordLength: 2,
}); // 'cl'
```

`null` e `undefined` retornam `''`. Argumentos invalidos geram `TypeError` ou
`RangeError`, inclusive para entrada vazia. Mapas sao objetos simples de
strings; valores sao resultados literais, `''` remove uma palavra.

O modo padrao `universal` nao aceita mapa. Limites inteiros positivos
`minWordLength` (3), `preserveWordLength` (3) e `maxWordLength` (4) sao
independentes e exclusivos de `configurable`. Palavras preservadas e
substituicoes nao sao truncadas. Nenhum argumento e modificado.

Esta heuristica nao traduz palavras nem garante unicidade. Conta pontos de
codigo Unicode, preserva a inicial e remove vogais do restante das palavras
comprimidas. `code` vira `cd` e `the` permanece `the` por padrao.

Desenvolvimento: `npm ci`, `npm test`, `npm run typecheck`,
`node test/package-smoke.cjs`. Os testes de contrato usam o corpus na raiz
do monorepositorio; o pacote instalado nao depende dele.
