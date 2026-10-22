// Builds decks to HTML (primary, accessible) and PDF (clean handout).
//
//   node scripts/build.mjs [deck folder or .md file ...] [--html-only] [--pptx]
//
// With no paths it builds every deck in decks/ and the layout gallery.
// Output is written next to each .md file. The accessibility check runs
// first and the build stops if it reports errors.
import { marpCli } from '@marp-team/marp-cli';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildTheme } from './theme.mjs';
import { checkDecks } from './check-accessibility.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(root);

const args = process.argv.slice(2);
const flags = new Set(args.filter((a) => a.startsWith('--')));
const paths = args.filter((a) => !a.startsWith('--'));

function inputs() {
  if (paths.length) {
    return paths.flatMap((p) => {
      const abs = resolve(p);
      return statSync(abs).isDirectory()
        ? readdirSync(abs).filter((f) => f.endsWith('.md') && f !== 'CREDITS.md').map((f) => join(abs, f))
        : [abs];
    });
  }
  const out = [];
  for (const d of existsSync('decks') ? readdirSync('decks') : []) {
    if (!statSync(join('decks', d)).isDirectory()) continue;
    for (const f of readdirSync(join('decks', d))) {
      if (f.endsWith('.md') && f !== 'CREDITS.md') out.push(join(root, 'decks', d, f));
    }
  }
  // The starter (template/slides.md) is full of placeholders; only the gallery is built.
  out.push(join(root, 'template', 'layout-gallery.md'));
  return out;
}

buildTheme();

const files = inputs();
if (checkDecks(files)) {
  console.error('\nBuild stopped: fix the accessibility errors above first.');
  process.exit(1);
}

const base = ['--config-file', join(root, '.marprc.yml'), '--no-stdin'];
const run = async (extra) => {
  const code = await marpCli([...base, ...extra, ...files]);
  if (code) process.exit(code);
};

await run([]);
// Keep speaker notes in Markdown and HTML. PDF exports contain no note annotations.
// Headings become PDF bookmarks. Include notes only when explicitly requested.
if (!flags.has('--html-only')) await run(['--pdf', '--pdf-outlines', ...(flags.has('--pdf-notes') ? ['--pdf-notes'] : [])]);
if (flags.has('--pptx')) {
  console.warn(
    '\nNote: Marp PPTX files contain each slide as a picture. They are not editable and ' +
      'screen readers cannot read them. Share the HTML or PDF for accessibility.',
  );
  await run(['--pptx']);
}
console.log(`\nBuilt ${files.length} deck(s).`);
