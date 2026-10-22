// Accessibility and copyright check for Marp decks in this folder.
//
//   node scripts/check-accessibility.mjs [deck folder or .md file ...]
//
// With no arguments it checks every deck in decks/ and template/*.md.
// Exits with code 1 when any ERROR is found; WARNINGs are advice.
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkCredits } from './credits.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// Marp image keywords that are stripped from alt text before rendering.
const IMAGE_KEYWORD =
  /^(bg|left|right|top|bottom|contain|cover|fit|auto|vertical|horizontal|\d+(\.\d+)?%|(left|right|top|bottom):\d+(\.\d+)?%|(w|h|width|height):\S+|(blur|brightness|contrast|drop-shadow|grayscale|hue-rotate|invert|opacity|saturate|sepia)(:\S+)?)$/i;
const DIRECTIVE =
  /^\s*_?(marp|theme|class|paginate|header|footer|backgroundColor|backgroundImage|backgroundPosition|backgroundRepeat|backgroundSize|color|style|size|headingDivider|lang|math|title|description|author|transition|fit)\s*(:|$)/;
const GENERIC_ALT =
  /^(image|img|picture|photo|figure|fig|chart|graph|diagram|screenshot|icon|logo|untitled|placeholder|alt|alt text)\s*\d*$/i;
const COMPLEX_ALT = /\b(chart|graph|plot|diagram|map|infographic|flowchart|timeline)\b/i;
const MAX_ALT = 250;
const MAX_WORDS = 110;

function findDecks(args) {
  if (args.length) {
    return args.flatMap((a) => {
      const p = resolve(a);
      if (statSync(p).isDirectory()) {
        return readdirSync(p).filter((f) => f.endsWith('.md') && f !== 'CREDITS.md').map((f) => join(p, f));
      }
      return [p];
    });
  }
  const out = [];
  const decks = join(root, 'decks');
  if (existsSync(decks)) {
    for (const d of readdirSync(decks)) {
      if (!statSync(join(decks, d)).isDirectory()) continue;
      for (const f of readdirSync(join(decks, d))) {
        if (f.endsWith('.md') && f !== 'CREDITS.md') out.push(join(decks, d, f));
      }
    }
  }
  const tpl = join(root, 'template');
  for (const f of readdirSync(tpl)) if (f.endsWith('.md') && f !== 'CREDITS.md') out.push(join(tpl, f));
  return out;
}

// Split a deck into front matter and slides, keeping line numbers.
function parse(text) {
  const lines = text.split(/\r?\n/);
  let i = 0;
  const front = {};
  if (lines[0] === '---') {
    for (i = 1; i < lines.length && lines[i] !== '---'; i++) {
      const m = lines[i].match(/^(\w+):\s*(.*)$/);
      if (m) front[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
    i++;
  }
  const slides = [];
  let cur = { start: i + 1, lines: [] };
  let fence = false;
  for (; i < lines.length; i++) {
    const l = lines[i];
    if (/^\s*(```|~~~)/.test(l)) fence = !fence;
    if (!fence && l === '---') {
      slides.push(cur);
      cur = { start: i + 2, lines: [] };
    } else {
      cur.lines.push(l);
    }
  }
  slides.push(cur);
  return { front, slides: slides.filter((s) => s.lines.some((l) => l.trim())) };
}

function check(file) {
  const problems = [];
  const rel = relative(root, file);
  const inTemplate = rel.startsWith('template');
  const report = (level, line, msg) => problems.push({ level, where: `${rel}:${line}`, msg });

  const text = readFileSync(file, 'utf8');
  const { front, slides } = parse(text);

  if (front.marp !== 'true') report('ERROR', 1, 'Front matter needs `marp: true`.');
  if (front.theme !== 'aalto') report('ERROR', 1, 'Front matter needs `theme: aalto`.');
  if (!front.lang) report('ERROR', 1, 'Front matter needs `lang:` (e.g. `lang: en`) so screen readers pick the right voice.');
  if (!front.title) report('ERROR', 1, 'Front matter needs `title:` (becomes the HTML/PDF document title).');

  for (const [key, value] of Object.entries(front)) {
    if (/\{\{[^}]*\}\}/.test(value) && !inTemplate)
      report('ERROR', 1, `Unfilled placeholder in front matter \`${key}\`.`);
  }

  let h1Count = 0;

  slides.forEach((slide, n) => {
    const at = (k) => slide.start + k;
    const body = slide.lines.join('\n');
    const comments = [...body.matchAll(/<!--([\s\S]*?)-->/g)].map((m) => m[1]);
    const notes = comments.filter((c) => !DIRECTIVE.test(c)).join('\n');
    const cls = (body.match(/<!--\s*_?class:\s*([^>]*?)-->/) || [, ''])[1];
    const visible = body.replace(/<!--[\s\S]*?-->/g, '');
    const label = `slide ${n + 1}`;

    // Headings: every slide needs one so screen-reader users can navigate.
    const mdHeadings = [...visible.matchAll(/^(#{1,6})\s+\S/gm)].map((m) => m[1].length);
    const htmlHeadings = [...visible.matchAll(/<h([1-6])\b/gi)].map((m) => Number(m[1]));
    const headings = [...mdHeadings, ...htmlHeadings];
    h1Count += headings.filter((h) => h === 1).length;
    if (!headings.some((h) => h <= 2)) {
      report(
        'ERROR',
        at(0),
        `${label} has no # or ## heading. For quote/statement slides add <h2 class="sr-only">Heading</h2>.`,
      );
    }

    let inFence = false;
    let inComment = false;
    slide.lines.forEach((raw, k) => {
      // Placeholders are expected in the template, nowhere else (notes included).
      if (/\{\{[^}]*\}\}/.test(raw) && !inTemplate)
        report('ERROR', at(k), `Unfilled placeholder: ${raw.match(/\{\{[^}]*\}\}/)[0]}`);

      // Only scan visible Markdown: skip code blocks, inline code and notes.
      if (/^\s*(```|~~~)/.test(raw)) {
        inFence = !inFence;
        return;
      }
      if (inFence) return;
      let line = '';
      let rest = raw;
      while (rest) {
        if (inComment) {
          const end = rest.indexOf('-->');
          if (end < 0) rest = '';
          else {
            rest = rest.slice(end + 3);
            inComment = false;
          }
        } else {
          const start = rest.indexOf('<!--');
          if (start < 0) {
            line += rest;
            rest = '';
          } else {
            line += rest.slice(0, start);
            rest = rest.slice(start + 4);
            inComment = true;
          }
        }
      }
      line = line.replace(/`[^`]*`/g, '');

      // Markdown images
      for (const m of line.matchAll(/!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/g)) {
        checkImage(m[1], m[2], at(k), notes, true);
      }
      // HTML images
      for (const m of line.matchAll(/<img\b[^>]*>/gi)) {
        const alt = m[0].match(/\balt\s*=\s*"([^"]*)"/i);
        const src = (m[0].match(/\bsrc\s*=\s*"([^"]*)"/i) || [, ''])[1];
        const decorative = /\baria-hidden\s*=\s*"true"|\brole\s*=\s*"presentation"/i.test(m[0]);
        if (!alt) report('ERROR', at(k), `<img src="${src}"> has no alt attribute.`);
        else if (decorative && alt[1] === '') continue;
        else checkImage(alt[1], src, at(k), notes, false);
      }
      // Inline SVG drawn in the slide
      for (const m of line.matchAll(/<svg\b[^>]*>/gi)) {
        if (/\baria-hidden\s*=\s*"true"/i.test(m[0])) continue;
        const label = m[0].match(/\baria-label\s*=\s*"([^"]*)"/i);
        if (!/\brole\s*=\s*"img"/i.test(m[0]) || !label)
          report('ERROR', at(k), 'Inline <svg> needs role="img" and aria-label="...", or aria-hidden="true" if decorative.');
        else checkImage(label[1], 'data:inline-svg', at(k), notes, false);
      }
      // Links
      for (const m of line.matchAll(/(?<!!)\[([^\]]*)\]\(([^)]+)\)/g)) {
        const t = m[1].trim();
        if (!t) report('ERROR', at(k), `Link to ${m[2]} has no text.`);
        else if (/^(click here|here|link|this|more|read more)$/i.test(t))
          report('WARNING', at(k), `Link text "${t}" does not say where it goes.`);
      }
      if (/<(video|audio)\b/i.test(line) && !/<track\b[^>]*kind\s*=\s*"(captions|subtitles)"/i.test(body))
        report('ERROR', at(k), 'Video/audio needs <track kind="captions" src="..."> (and a transcript in the notes).');
      const size = line.match(/font-size\s*:\s*(\d+(?:\.\d+)?)px/i);
      if (size && Number(size[1]) < 18)
        report('WARNING', at(k), 'Inline font size below 18px is hard to read in a room.');
      if (/(?<![-\w])color\s*:/i.test(line) && !/var\(--/.test(line))
        report('WARNING', at(k), 'Inline colour: check contrast is at least 4.5:1, or use a theme class.');
    });

    const words = visible
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
      .split(/\s+/)
      .filter((w) => /\w/.test(w)).length;
    if (words > MAX_WORDS)
      report('WARNING', at(0), `${label} has ${words} words; consider splitting it or moving detail to the notes.`);

    if (/\b(black|blue|red|yellow)\b/.test(cls) && /color\s*:\s*(#fff|white)/i.test(visible))
      report('ERROR', at(0), `${label}: white text on a coloured slide fails contrast; use the theme colours.`);

    function checkImage(rawAlt, src, line, notes, markdown) {
      const words = rawAlt.trim().split(/\s+/).filter(Boolean);
      const isBg = markdown && words.some((w) => w.toLowerCase() === 'bg');
      const alt = (markdown ? words.filter((w) => !IMAGE_KEYWORD.test(w)) : words).join(' ').trim();

      if (!/^(https?:|data:)/i.test(src)) {
        const p = resolve(dirname(file), decodeURI(src));
        if (!existsSync(p)) report('ERROR', line, `Image not found: ${src}`);
      }
      if (!alt) {
        if (isBg) report('WARNING', line, `Background image ${src} has no description. Fine only if it is purely decorative.`);
        else report('ERROR', line, `Image ${src} has no alt text. Describe what it shows and why it is on the slide.`);
        return;
      }
      if (/\.(png|jpe?g|gif|svg|webp|bmp|tiff?)$/i.test(alt) || alt === src)
        report('ERROR', line, `Alt text "${alt}" is a file name, not a description.`);
      else if (GENERIC_ALT.test(alt)) report('ERROR', line, `Alt text "${alt}" is too generic.`);
      if (/^(an? )?(image|picture|photo|graphic) of\b/i.test(alt))
        report('WARNING', line, 'Start alt text with the content; screen readers already say "image".');
      if (alt.length > MAX_ALT)
        report('WARNING', line, `Alt text is ${alt.length} characters. Keep it under ${MAX_ALT} and move detail to "Figure description:" in the notes.`);
      if (COMPLEX_ALT.test(alt) && !/figure description\s*:/i.test(notes))
        report('ERROR', line, 'Charts and diagrams need a "Figure description:" in this slide\'s speaker notes giving the data or structure.');
    }
  });

  checkCredits(file, slides, report, inTemplate);

  if (h1Count !== 1)
    report('WARNING', 1, `Deck has ${h1Count} level-1 headings; use one # (the title slide) and ## for every other slide.`);

  return problems;
}

export function checkDecks(args = []) {
  const files = findDecks(args);
  const problems = files.flatMap(check);
  for (const p of problems) console.log(`${p.level.padEnd(7)} ${p.where}  ${p.msg}`);
  const errors = problems.filter((p) => p.level === 'ERROR').length;
  const warnings = problems.length - errors;
  console.log(`\nChecked ${files.length} deck(s): ${errors} error(s), ${warnings} warning(s).`);
  return errors;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  process.exitCode = checkDecks(process.argv.slice(2)) ? 1 : 0;
}
