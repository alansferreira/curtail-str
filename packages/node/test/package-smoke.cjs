const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createRequire } = require('node:module');

const source = path.resolve(__dirname, '..');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'curtail-str-node-'));
try {
  const packed = JSON.parse(execFileSync('npm', [
    'pack', '--json', '--pack-destination', temporary,
  ], { cwd: source, encoding: 'utf8' }));
  execFileSync('npm', [
    'install', '--prefix', temporary, '--ignore-scripts', '--no-audit', '--no-fund',
    path.join(temporary, packed[0].filename),
  ], { stdio: 'pipe' });
  const requireInstalled = createRequire(path.join(temporary, 'consumer.cjs'));
  assert.equal(requireInstalled('curtail-str')
    .curtailStr('codigo'), 'cdg');
  assert.equal(requireInstalled('curtail-str/curtail-str.min.js')
    .curtailStr('codigo'), 'cdg');
  execFileSync(process.execPath, ['--input-type=module', '-e', `
    import { curtailStr as shorten } from 'curtail-str';
    import { curtailStr as shortenMin } from 'curtail-str/curtail-str.min.mjs';
    if (shorten('codigo') !== 'cdg') throw new Error('ESM package import failed');
    if (shortenMin('codigo') !== 'cdg') throw new Error('Minified ESM package import failed');
  `], { cwd: temporary, stdio: 'inherit' });
  for (const file of ['consumer.cts', 'consumer.mts']) {
    fs.copyFileSync(path.join(__dirname, file), path.join(temporary, file));
  }
  execFileSync(process.execPath, [
    path.join(source, 'node_modules/typescript/bin/tsc'), '--noEmit', '--strict',
    '--module', 'NodeNext', '--moduleResolution', 'NodeNext', '--target', 'ES2022',
    'consumer.cts', 'consumer.mts',
  ], { cwd: temporary, stdio: 'inherit' });
  console.log('Installed tarball: CommonJS, ESM and TypeScript OK');
} finally {
  fs.rmSync(temporary, { recursive: true });
}
