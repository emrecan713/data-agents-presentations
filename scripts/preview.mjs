// Live preview: serves every deck at http://localhost:8090 and re-renders on save.
import { marpCli } from '@marp-team/marp-cli';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildTheme } from './theme.mjs';

process.chdir(resolve(dirname(fileURLToPath(import.meta.url)), '..'));
process.env.PORT ||= '8090';
buildTheme();
console.log(`Open http://localhost:${process.env.PORT}/ and pick a deck (Ctrl+C to stop).`);
process.exitCode = await marpCli(['--config-file', '.marprc.yml', '--server', '.']);
