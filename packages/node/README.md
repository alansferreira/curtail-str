# Abbrev para Node.js

Node.js 22 ou superior. Pacote local, sem dependencias de runtime.
O nome `abbrev` ja esta ocupado no registro npm por outro projeto.
Instale este pacote pelo caminho local, nao com `npm install abbrev`.
Os imports abaixo resolvem o pacote local instalado. Uma futura publicacao
exigira um nome com escopo disponivel.

```js
import { abbrev } from 'abbrev';
// CommonJS: const { abbrev } = require('abbrev');

abbrev('codigo-do-cliente'); // 'cdg-clnt'
abbrev('code-in-the-stock', {
  mode: 'custom',
  replacements: { the: '', code: 'cdg' },
}); // 'cdg-stck'
abbrev('cliente', {
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
