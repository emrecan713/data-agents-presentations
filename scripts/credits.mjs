// Copyright and licence checks for one deck. Called by check-accessibility.mjs.
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const LICENCES = [
  /^own work$/i,
  /^ai-generated$/i,
  /^cc0$/i,
  /^public domain$/i,
  /^cc by(-sa)? \d\.\d$/i,
  /^permission$/i,
  /^aalto brand$/i,
];
const NEEDS_CREDIT = /^(ai-generated|cc by.*|permission)$/i;
const LICENCE_LABEL = /CC BY 4\.0/;

const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ').trim();

// Reads the first Markdown table with File and Licence columns.
function readCredits(path) {
  const rows = new Map();
  const lines = readFileSync(path, 'utf8').split(/\r?\n/);
  let header = null;
  for (const line of lines) {
    if (!line.trim().startsWith('|')) {
      if (header && rows.size) break;
      continue;
    }
    const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
    if (!header) {
      const lower = cells.map((c) => c.toLowerCase());
      if (lower.includes('file') && lower.includes('licence')) header = lower;
      continue;
    }
    if (cells.every((c) => /^:?-+:?$/.test(c))) continue;
    const row = Object.fromEntries(header.map((h, i) => [h, cells[i] ?? '']));
    rows.set(row.file.replace(/`/g, ''), row);
  }
  return rows;
}

function usedAssets(body) {
  const visible = body.replace(/<!--(?!\s*_?footer)[\s\S]*?-->/g, '').replace(/```[\s\S]*?```/g, '').replace(/`[^`]*`/g, '');
  const srcs = [
    ...[...visible.matchAll(/!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/g)].map((m) => m[1]),
    ...[...visible.matchAll(/<(?:img|source|video|audio)\b[^>]*\bsrc\s*=\s*"([^"]+)"/gi)].map((m) => m[1]),
  ];
  return [...new Set(srcs)];
}

export function checkCredits(file, slides, report, inTemplate) {
  const creditsPath = join(dirname(file), 'assets', 'CREDITS.md');
  const credits = existsSync(creditsPath) ? readCredits(creditsPath) : null;
  let missingFileReported = false;

  slides.forEach((slide, n) => {
    const body = slide.lines.join('\n');
    const label = `slide ${n + 1}`;

    if (n === 0 && !LICENCE_LABEL.test(body)) {
      report(
        inTemplate ? 'WARNING' : 'ERROR',
        slide.start,
        'Title slide needs the open licence line, e.g. <!-- _footer: "© 2026 Emrecan Gülay · CC BY 4.0, except logos, quotations and material credited to others" -->.',
      );
    }

    for (const src of usedAssets(body)) {
      if (/^(https?:)?\/\//i.test(src)) {
        report('ERROR', slide.start, `${label} uses a web image (${src}). Save it in assets/ and record its source and licence.`);
        continue;
      }
      if (/^data:/i.test(src)) continue;
      const key = decodeURI(src).replace(/^\.?\/?assets\//, '');
      if (!credits) {
        if (!missingFileReported)
          report('ERROR', slide.start, 'Deck uses assets but has no assets/CREDITS.md with their sources and licences.');
        missingFileReported = true;
        continue;
      }
      const row = credits.get(key);
      if (!row) {
        report('ERROR', slide.start, `${label}: ${key} has no row in assets/CREDITS.md (source, creator, licence).`);
        continue;
      }
      const licence = row.licence || '';
      if (!LICENCES.some((re) => re.test(licence))) {
        report('ERROR', slide.start, `${label}: ${key} has licence "${licence}", which is not an allowed licence. Leave it out or find a usable source.`);
        continue;
      }
      if (NEEDS_CREDIT.test(licence)) {
        const credit = row['credit line'] || '';
        if (!credit) report('ERROR', slide.start, `${key} (${licence}) needs a credit line in assets/CREDITS.md.`);
        else if (!norm(body).includes(norm(credit)))
          report('ERROR', slide.start, `${label} shows ${key} (${licence}) but not its credit line: "${credit}".`);
      }
    }
  });
}
