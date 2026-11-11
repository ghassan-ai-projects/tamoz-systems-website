# Tamoz Systems website

Static website for [tamoz-systems.com](https://tamoz-systems.com), published with GitHub Pages.

Tamoz is a physical AI agent for the equipment you already run: it watches sensors, works out what is likely happening when a machine does something unexpected, says how sure it is, and proposes a response from actions the team has defined. The site is in a testing phase, so it is built to be changed quickly.

## Structure

| Path | Purpose |
|---|---|
| `index.html` | The live page served by GitHub Pages. A copy of one design, so don't edit it directly. |
| `designs/homepage.html` | General homepage (sites such as cold chain, data centres, EV charging, farms). |
| `designs/manufacturing.html` | "Tamoz for Manufacturing" (press hall, compressed air, CNC, process water, ovens). |
| `designs/conveyor.html` | "Tamoz for belt conveyors" (multi-drive belt conveyors in mining, aggregates, cement, ports, power and bulk terminals). Its animation replays one simulated test day. |
| `switch.sh` | Chooses which design is live. |
| `scripts/seo.py` | SEO/GEO pass: title, description, canonical, Open Graph, JSON-LD (incl. FAQ), hidden H1 keywords. Re-run after editing a design. |
| `fonts/`, `img/`, `favicon.ico` | Self-hosted fonts, OG image and icons. |
| `robots.txt`, `sitemap.xml`, `llms.txt` | Crawler, sitemap and AI-assistant summary files. Update `lastmod` and `llms.txt` when content changes. |
| `CNAME` | Custom domain for GitHub Pages. Don't delete it. |

Each design is a single HTML file with inline CSS and JS. Fonts are self-hosted in `fonts/` (no requests to Google). There is no build step.

## Workflow

1. Edit the design in `designs/`.
2. Run `python3 scripts/seo.py` (titles and descriptions live in its `CONFIG`).
3. Make it live:

   ```bash
   ./switch.sh homepage        # or: manufacturing, conveyor
   git add -A && git commit -m "Update design" && git push
   ```

   `./switch.sh <design> --push` switches, commits and pushes in one step.

Pages redeploys about a minute after each push.

To add another variant, drop a new `designs/<name>.html` and run `./switch.sh <name>`.

## Preview locally

```bash
python3 -m http.server 8765
```

Then open <http://127.0.0.1:8765/> for the live page, or `/designs/<name>.html` for a specific design.

## Known gaps

- The pilot request form posts to Formspree (`https://formspree.io/f/mjywbebj`) with `fetch`, and without JS it posts directly. Submissions go to the inbox set in the Formspree dashboard. The form still needs a privacy note and a privacy page.
- The designs are separate copies, so a change that should apply to all of them has to be made in each file.
- `designs/conveyor.html` cites two pages that are not live yet: source 3 (the personal-site conveyor page) and source 4 (`WEBSITE.md` on the streams-simulator `belt-m4-evidence` branch). Update both links once they are merged.

## Related

- Project write-up, use cases, technical deep dive and evidence: the Tamoz pages on the author's personal site.
- Source: <https://github.com/ghassan-ai-projects/tamoz>
