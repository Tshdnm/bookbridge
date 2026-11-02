import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const root = path.dirname(fileURLToPath(import.meta.url));
const modules = process.env.TASK3_NODE_MODULES || path.resolve('node_modules');
const require = createRequire(path.join(modules, 'package.json'));
const { instance } = require('@viz-js/viz');
const sharp = require('sharp');
const viz = await instance();
const manifest = JSON.parse(await fs.readFile(path.join(root, 'manifest.json'), 'utf8'));
await fs.mkdir(path.join(root, 'previews'), { recursive: true });
for (const model of manifest.models) {
  const dot = await fs.readFile(path.join(root, model.dot), 'utf8');
  const svg = viz.renderString(dot, { engine: model.engine, format: 'svg' });
  await fs.writeFile(path.join(root, model.svg), svg, 'utf8');
  await sharp(Buffer.from(svg)).resize({ width: 1400 }).png().toFile(path.join(root, 'previews', model.svg.replace('.svg','.png')));
  console.log(`${model.id}: ${model.svg}`);
}
