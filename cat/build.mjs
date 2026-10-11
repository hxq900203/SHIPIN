// 打包成单文件 index.js，并生成 index.js.md5 / index.config.js(.md5)
import { build } from 'esbuild';
import { createHash } from 'crypto';
import { readFileSync, writeFileSync, mkdirSync } from 'fs';

const out = '../dist/cat';
mkdirSync(out, { recursive: true });

await build({
    entryPoints: ['src/index.js'],
    outfile: `${out}/index.js`,
    bundle: true,
    minify: true,
    platform: 'node',
    format: 'esm',
    target: 'node18',
    legalComments: 'none',
    banner: { js: "import { createRequire } from 'module'; const require = createRequire(import.meta.url);" },
});
writeFileSync(`${out}/index.config.js`, 'export default {};\n');

for (const f of ['index.js', 'index.config.js']) {
    const md5 = createHash('md5').update(readFileSync(`${out}/${f}`)).digest('hex');
    writeFileSync(`${out}/${f}.md5`, md5);
    console.log(f, md5);
}
