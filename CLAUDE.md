# leandrobentancur.github.io — how this repo works

Leandro Bentancur's academic site, rendered from one hand-edited data set.
**The whole point is that a fact is written down exactly once.** Before adding
a field, a file or a page, check whether the fact already exists somewhere in
`data/`.

**This repository is public, and it is half of a pair.** Its sibling
`../cv-build/` builds the LaTeX CVs from this same `data/`, and is deliberately
not under version control: a CV is not something this site publishes. The split
is the privacy boundary, not a filing preference — personal data, CV PDFs and
the ANII export live over there, and nothing in this repo can read them.

## The three tiers

1. **Truth — hand-edited.** `data/*.yml` and `content/*.md`. The only files a
   human ever edits.
2. **Derived — never hand-edited.** `docs/` (the site), `assets/` (web-sized
   images), `reports/`, and `../cv-build/out/` (the PDFs). Deleting them loses
   nothing; `make all` rebuilds them. Never fix a typo here — fix it in tier 1.
3. **External, one-way.** CVUy at ANII. It is the most complete record and it
   cannot be written to programmatically. It is imported to a read-only
   snapshot and compared, never rendered from. The snapshot is gitignored: it
   is someone's official record plus notes on its defects, and only
   `make reconcile` — which runs locally, never in CI — reads it.

## The update system, part by part

| Part | Edit | When | Then run |
|---|---|---|---|
| Conferences, talks, visits | `data/events.yml` | after each trip, or the day a future one is agreed | `make site` |
| Papers | `data/publications.yml` | new preprint, acceptance, publication | `make site`, then `cd ../cv-build && make` |
| Courses | `data/teaching.yml` — add an offering to the existing course id | start of each semester | `make site`, then `cd ../cv-build && make` |
| Appointments | `data/positions.yml` | new grado or contract | `cd ../cv-build && make` (CV only) |
| Research framing | `data/research.yml` + `content/research/<id>.{en,es}.md` | when a line starts or ends | `make site`, then `cd ../cv-build && make` |
| Bio prose | `content/bio.{en,es}.md` | rarely | `make site` |
| Photos | `build/make_images.py` recipe + originals in `../Pics/` | new photo | `make images site`, then commit `assets/` |
| A tailored CV | new file in `../cv-build/profiles/` (~15 lines) | per application | `cd ../cv-build && make` |
| C.I., date of birth | `../cv-build/private.yml` (outside git) | almost never | `cd ../cv-build && make` |
| CVUy at ANII | export the .txt, then type the report's list into the web form by hand | before a llamado or renovación | `make reconcile` |

Lost? `make status` prints what is complete, what is pending and what the
validator is complaining about.

The same system, written for Leandro rather than for you, with a copy-pasteable
recipe per situation: **[ACTUALIZAR.md](ACTUALIZAR.md)**. Keep the two in step —
if a rule changes here, change it there.

## Rules that are not negotiable

- **`docs/` is generated.** Editing it is always a bug.
- **Dates are month-precision in public.** `YYYY-MM`, or `YYYY` when the month
  is genuinely unknown. Never day ranges — he asked for this explicitly.
- **The repository is public, so "private" cannot mean a flag.** Anything a
  stranger must not read is absent from the repo, not marked inside it.
  Personal data and the CVs are in `../cv-build/`, outside git entirely; the
  ANII mirror `data/_cvuy_snapshot.yml` is gitignored. An event that is not
  publicly announced is not recorded here at all — not even flagged — because
  a committed row is readable whether or not it is rendered, and git history
  keeps it after a delete. Ask before adding anything of the kind.
- **The PhD thesis title registered at ANII is the dropped one** ("Jerarquías
  poliedrales…"). The current framing is Christoffel–Darboux kernels and
  density recovery. The validator fails the build if the old title reappears.
- **Never render from the CVUy snapshot.** It lags and has its own data-entry
  errors (a `http://https://` URL, SOLACE dated 2026 when it was 2025).
- **One id per thing.** A course that acquires a second name gets a
  `public_title`, not a second entry. That rule is why "Cadenas de Markov
  Controladas" stopped having four names.
- **i18n:** a field is either a scalar (English) or `{en:, es:}`. In
  `events.yml` use the `name` / `name_es` override form. Quote any value
  containing a comma — YAML flow mappings split on commas and silently eat half
  the value. The validator now catches this.

## Design

Typeset: Source Serif 4 throughout, ink `#1B1E24` on paper `#FCFBF8`, accent
ink-blue `#2A3F63`, hairline rules, no cards, no motion. The masthead mark is
the N=12 logarithmic Fekete configuration — the icosahedron — generated in
`build/motif.py` from real vertex coordinates. Full palette and dark variant in
`site/static/style.css`; tokens only, never a literal colour in a rule.

## Layout

```
data/        truth, hand-edited YAML (data/_*.yml gitignored)
content/     long-form prose, bilingual markdown
site/        templates, strings.yml (all UI wording), static/style.css
build/       render_site · validate · make_images · import_cvuy · reconcile · status
docs/        generated site, deployed by GitHub Actions

../cv-build/ not in git: render_cv.py, profiles/, templates/, out/, private.yml
```

## Pages

All four exist in both languages: `/`, `/research/`, `/publications/`,
`/teaching/`, and the same under `/es/`. URL slugs stay English in both
languages so links never break when wording changes.

Adding a page: template in `site/templates/`, a branch in `context_for()`, the
name in `BUILT` and `PAGES` in `build/render_site.py`, its heading in
`TITLES`, and its wording in `site/strings.yml`. Nav links to a page not in
`BUILT` resolve to `#` rather than to a 404.

Templates run with `StrictUndefined`: an optional key must be probed with
`p.get('doi')`, never `p.doi`, or the build dies on the entry that lacks it.
