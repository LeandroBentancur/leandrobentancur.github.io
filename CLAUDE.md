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
| What the homepage shows as news | `featured: true` on a row of `data/events.yml` | when something stops being news, or starts | `make site` |
| Papers | `data/publications.yml` | new preprint, acceptance, publication | `make site`, then `cd ../cv-build && make` |
| Courses | `data/teaching.yml` — add an offering to the existing course id | start of each semester | `cd ../cv-build && make` (CV only) |
| Appointments | `data/positions.yml` | new grado or contract | `cd ../cv-build && make` (CV only) |
| Research framing | `data/research.yml` + `content/research/<id>.{en,es}.md` | when a line starts or ends | `make site`, then `cd ../cv-build && make` |
| Bio prose | `content/bio.{en,es}.md` | rarely | `make site` |
| Photos | `build/make_images.py` recipe + originals in `../Pics/` | new photo | `make images site`, then commit `assets/` |
| A tailored CV | new file in `../cv-build/profiles/` (~15 lines) | per application | `cd ../cv-build && make` |
| C.I., date of birth | `../cv-build/private.yml` (outside git) | almost never | `cd ../cv-build && make` |
| CVUy at ANII | export the .txt, then type the report's list into the web form by hand | before a llamado or renovación | `make reconcile` |
| The site's own URL | `site_url` in `data/person.yml` | only if the site moves to a custom domain | `make site` |

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
- **The dropped PhD title must never come back.** "Jerarquías poliedrales…"
  was abandoned; the framing is Christoffel–Darboux kernels and density
  recovery, and the validator fails the build if the old title reappears.
  ANII itself is no longer wrong about this — the live CVUy export, checked on
  2026-09-16, registers the new title — but `data/_cvuy_snapshot.yml` and
  `reports/cvuy-drift.md` come from a May 2026 export and still claim it is.
  **Re-export before believing a drift report**, and never repeat its claims
  about ANII without checking the live record.
- **Never render from the CVUy snapshot.** It lags and has its own data-entry
  errors (a `http://https://` URL, SOLACE dated 2026 when it was 2025).
- **One id per thing.** A course that acquires a second name gets a
  `public_title`, not a second entry. That rule is why "Cadenas de Markov
  Controladas" stopped having four names.
- **The homepage news list is hand-picked, not computed.** Only rows carrying
  `featured: true` reach it; recency decides the order, never the membership.
  Do not quietly re-add a recency rule because the list looks short — he asked
  to choose the items himself. Unfeaturing hides a row from the homepage and
  from nowhere else: it stays in the talks list and in the CVs.
- **i18n:** a field is either a scalar (English) or `{en:, es:}`. In
  `events.yml` use the `name` / `name_es` override form. Quote any value
  containing a comma — YAML flow mappings split on commas and silently eat half
  the value. The validator now catches this.

## Design

Typeset: Source Serif 4 throughout, ink `#1B1E24` on paper `#FCFBF8`, accent
ink-blue `#2A3F63`, hairline rules, no cards, no motion. The masthead mark is
the N=12 logarithmic Fekete configuration — the icosahedron — generated in
`build/motif.py` from real vertex coordinates. Full palette and dark variant in
`site/static/style.css`; tokens only, never a literal colour in a rule. Prose
and figures share one measure, the `--measure` token — a photo is never wider
than the text beside it.

**The typeface is served from this origin.** `site/static/fonts/` holds the six
woff2 cuts (normal 400/600 and italic 400, latin and latin-ext), committed, and
`render_site.py` copies them to `docs/fonts/`. The Google Fonts link is gone on
purpose: it made every visitor fetch from a third party before a word rendered.
The `@font-face` rules are at the top of `style.css` — do not re-add the CDN.

**Every page carries a canonical URL, an `hreflang` pair and Open Graph tags**,
all derived from `site_url` in `person.yml`. `descriptions` in `strings.yml`
gives the inner pages their own one-line summary; the homepage uses the tagline.

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

Three, in both languages: `/`, `/research/` and `/publications/`, and the same
under `/es/`. URL slugs stay English in both languages so links never break when
wording changes.

A **teaching page** existed and was withdrawn on 2026-09-16: it listed courses
and appointments, which a visitor can get from the CV, and it will come back
only when there are materials of his own worth publishing. `data/teaching.yml`
and `data/positions.yml` stay — the CVs read them. The template, its prose and
the model functions that fed it (`courses_by_institution`, `positions`,
`current_course`, and `attended` for the conference list) are in the history:
`git show 1e0574e:site/templates/teaching.html.j2`. Rebuild from those rather
than from memory.

Adding a page: template in `site/templates/`, a branch in `context_for()`, the
name in `BUILT` and `PAGES` in `build/render_site.py`, its heading in
`TITLES`, its wording in `site/strings.yml`, and a nav link in `base.html.j2`.
Nav links to a page not in `BUILT` resolve to `#` rather than to a 404.
Removing one is the same list in reverse; `render_site.py` deletes the stale
directory under `docs/` on the next build, so nothing keeps being served.

Templates run with `StrictUndefined`: an optional key must be probed with
`p.get('doi')`, never `p.doi`, or the build dies on the entry that lacks it.
