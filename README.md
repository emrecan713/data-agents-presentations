# What are we working with? Qualitative research with AI

Teaching materials and presentations on AI in qualitative research, by Emrecan Gülay, Aalto University.

## Presentations

### Qualitative research with AI · Thursday 22 October 2026

[Read the presentation (PDF)](decks/Thursday%2022%20October%202026%20-%20Qualitative%20research%20with%20AI/Thursday%2022%20October%202026%20-%20Qualitative%20research%20with%20AI.pdf) · [Browse the slides, sources and credits](decks/Thursday%2022%20October%202026%20-%20Qualitative%20research%20with%20AI)

The PDF can be read or downloaded directly on GitHub. To use the HTML slides, download the repository and open the presentation's `.html` file. Keep its `assets/` folder beside it.

## Edit and build the materials

The presentations use Markdown and Marp with the Aalto University theme. Each deck builds into HTML slides and a PDF handout.

Double-click `start.bat`. It installs the tools on first run (needs Node.js) and offers:

1. **Preview**: opens a live preview at http://localhost:8090 that updates when you save.
2. **New deck**: asks for the purpose and date, and creates a deck named like `decks/Tuesday 20 October 2026 - Data Agents workshop/` from the template.
3. **Check accessibility**: lists missing alt text, headings and other problems.
4. **Build**: writes an HTML and a PDF with the deck's name next to every deck.

For editing with a live side-by-side preview, open this folder in VS Code with the *Marp for VS Code* extension. The settings in `.vscode/` load the Aalto theme.

## Where things are

- `decks/`: one folder per presentation, with its images in `assets/`.
- `template/layout-gallery.md`: every available layout. Build it and open `layout-gallery.html` to see them.
- `template/slides.md`: the starting point for new decks.
- `theme/`: the Aalto theme. Colours, Arial typography, margins and logos come from the official Aalto University PowerPoint masters (June 2026 edition, as used in *Qualitative Research and AI – v04 Aalto*).

## Open licence

Everything here is published openly: slide content under CC BY 4.0 and code under MIT. Logos, participant quotations and third-party material are excluded. See `LICENSE.md`.

## Accessibility

Every image needs alt text, and charts and diagrams also need a written figure description in the speaker notes. The checker enforces this and the build stops until it passes. The HTML version is the one to share with people using screen readers. Marp's PowerPoint export saves slides as pictures, so use it only when PowerPoint is required.
