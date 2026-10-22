// Builds theme/aalto.css from theme/aalto.src.css by embedding the logo SVGs
// (black and white versions), so every deck renders the logo wherever its
// HTML or PDF ends up.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const themeDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'theme');

const dataUri = (file, colour) => {
  const svg = readFileSync(join(themeDir, 'logos', file), 'utf8')
    .trim()
    .replaceAll('currentColor', colour)
    .replaceAll('"', "'")
    .replace(/[#<>%]/g, encodeURIComponent);
  return `url("data:image/svg+xml,${svg}")`;
};

export function buildTheme() {
  const css = readFileSync(join(themeDir, 'aalto.src.css'), 'utf8')
    .replace(
      '/*!',
      '/*!\n * GENERATED FILE: do not edit. Edit aalto.src.css and run `npm run theme`.\n *',
    )
    .replace('@theme aalto-source', '@theme aalto')
    .replaceAll('__LOGO_A_WHITE__', dataUri('aalto-a.svg', '#fff'))
    .replaceAll('__LOGO_A__', dataUri('aalto-a.svg', '#000'))
    .replaceAll('__LOGO_FULL_WHITE__', dataUri('aalto-full.svg', '#fff'))
    .replaceAll('__LOGO_FULL__', dataUri('aalto-full.svg', '#000'));
  writeFileSync(join(themeDir, 'aalto.css'), css);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  buildTheme();
  console.log('theme/aalto.css updated');
}
