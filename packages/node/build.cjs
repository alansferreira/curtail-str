'use strict';

const fs = require('node:fs');
const path = require('node:path');
const esbuild = require('esbuild');

const root = __dirname;
const dist = path.join(root, 'dist');
const source = fs.readFileSync(path.join(root, 'index.cjs'), 'utf8');
const footer = 'module.exports = { curtailStr };';

if (!source.endsWith(`${footer}\n`)) {
  throw new Error('Unexpected index.cjs export footer');
}

const body = source.slice(0, -`${footer}\n`.length);
const umdSource = `(function (root, factory) {
  if (typeof exports === 'object' && typeof module === 'object') {
    module.exports = factory();
  } else if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof exports === 'object') {
    exports.curtailStr = factory().curtailStr;
  } else {
    root.curtailStr = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : typeof self !== 'undefined' ? self : this, function () {
${body}  return { curtailStr };
});
`;
const esmSource = `${body}export { curtailStr };\n`;

const umd = esbuild.transformSync(umdSource, {
  loader: 'js',
  target: 'es2022',
  minify: true,
  legalComments: 'none',
});
const esm = esbuild.transformSync(esmSource, {
  loader: 'js',
  format: 'esm',
  target: 'es2022',
  minify: true,
  legalComments: 'none',
});

fs.mkdirSync(dist, { recursive: true });
fs.writeFileSync(path.join(dist, 'curtail-str.min.js'), umd.code);
fs.writeFileSync(path.join(dist, 'curtail-str.min.mjs'), esm.code);
