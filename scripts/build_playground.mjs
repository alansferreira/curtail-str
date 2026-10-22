import { mkdir, readFile, copyFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const output = new URL('playground/dist/', root);
const source = await readFile(new URL('packages/node/index.cjs', root), 'utf8');
const footer = 'module.exports = { curtailStr };';
if (!source.endsWith(`${footer}\n`)) {
  throw new Error('Unexpected Node.js export: update the playground browser build');
}
await mkdir(output, { recursive: true });
for (const name of ['index.html', 'styles.css', 'app.mjs']) {
  await copyFile(new URL(`playground/${name}`, root), new URL(name, output));
}
await writeFile(new URL('core.mjs', output), source.slice(0, -`${footer}\n`.length) +
  'export { curtailStr };\n');
await copyFile(new URL('LICENSE', root), new URL('LICENSE', output));
await writeFile(new URL('.nojekyll', output), '');
console.log(`Playground built: ${fileURLToPath(output)}`);
