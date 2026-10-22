// Starts a new deck from template/slides.md, named by its date and purpose.
//
//   node scripts/new-deck.mjs "Purpose" [--date YYYY-MM-DD]
//
// Creates decks/<Weekday D Month YYYY> - <Purpose>/ with a deck file of the same
// name and assets/CREDITS.md. Without --date the deck is "Undated - <Purpose>".
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const dateFlag = args.indexOf('--date');
const iso = dateFlag >= 0 ? args.splice(dateFlag, 2)[1] : null;
const purpose = args.join(' ').replace(/[<>:"/\|?*]/g, '').replace(/\s+/g, ' ').trim();

if (!purpose || (iso !== null && !/^\d{4}-\d{2}-\d{2}$/.test(iso ?? ''))) {
  console.error('Usage: node scripts/new-deck.mjs "Purpose" [--date YYYY-MM-DD]');
  process.exit(1);
}

let dateWords = 'Undated';
let year = String(new Date().getFullYear());
if (iso) {
  const d = new Date(`${iso}T12:00:00`);
  const part = (o) => d.toLocaleDateString('en-GB', o);
  dateWords = `${part({ weekday: 'long' })} ${d.getDate()} ${part({ month: 'long' })} ${d.getFullYear()}`;
  year = iso.slice(0, 4);
}

const name = `${dateWords} - ${purpose}`;
const folder = join(root, 'decks', name);
if (existsSync(folder)) {
  console.error(`Already exists: decks/${name}`);
  process.exit(1);
}

mkdirSync(join(folder, 'assets'), { recursive: true });
let md = readFileSync(join(root, 'template', 'slides.md'), 'utf8')
  .replaceAll('{{purpose}}', purpose)
  .replaceAll('{{year}}', year);
if (iso) md = md.replaceAll('{{date}}', dateWords);
writeFileSync(join(folder, `${name}.md`), md);
writeFileSync(join(folder, 'assets', 'CREDITS.md'), readFileSync(join(root, 'template', 'CREDITS.md'), 'utf8'));

console.log(`Created decks/${name}/${name}.md`);
