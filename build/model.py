"""Loads data/ and content/ and answers the questions the templates ask.
Nothing here writes; nothing downstream reads YAML directly."""
import datetime
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("en", "es")
MONTHS = {
    "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["", "ene", "feb", "mar", "abr", "may", "jun",
           "jul", "ago", "set", "oct", "nov", "dic"],
}


def _read(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def load():
    # data/_*.yml are read-only snapshots of external systems, not part of the
    # model — reconcile.py loads them itself. Nothing here reads personal data:
    # the C.I. and date of birth live in ../cv-build/private.yml, outside this
    # repository, and only the CV renderer there ever opens them.
    data = {p.stem: _read(p) for p in sorted((ROOT / "data").glob("*.yml"))
            if not p.stem.startswith("_")}
    data["strings"] = _read("site/strings.yml")
    return data


def content(name, lang):
    """content/<name>.<lang>.md, rendered. Falls back to English if a Spanish
    file is missing, so a half-translated site still builds and says so."""
    import md
    path = ROOT / "content" / f"{name}.{lang}.md"
    if not path.exists():
        path = ROOT / "content" / f"{name}.en.md"
    return md.render(path.read_text(encoding="utf-8"))


def t(value, lang):
    """A field is either a scalar or an {en: , es: } mapping."""
    if isinstance(value, dict):
        return value.get(lang) or value.get("en") or ""
    return value if value is not None else ""


def field(entry, name, lang):
    """The scalar + _es override convention used across events.yml."""
    if lang != "en" and entry.get(f"{name}_{lang}"):
        return entry[f"{name}_{lang}"]
    return t(entry.get(name), lang)


def ym(value):
    """YYYY-MM or YYYY, from YAML's string or int, to a sortable (year, month)."""
    if value is None:
        return (0, 0)
    s = str(value)
    if "-" in s:
        y, m = s.split("-")[:2]
        return (int(y), int(m))
    return (int(s), 0)


def fmt_date(value, lang):
    y, m = ym(value)
    return f"{MONTHS[lang][m]} {y}" if m else str(y)


def is_upcoming(value, today=None):
    today = today or datetime.date.today()
    y, m = ym(value)
    if not m:                      # a year-only date is only future if the year is
        return y > today.year
    return (y, m) > (today.year, today.month)


def news(data, lang):
    """The homepage list, chosen by hand: an event appears only if it carries
    `featured: true`. Recency is not the rule — he marks what counts as news and
    unmarks it when it stops being. Upcoming first and marked; then the rest,
    most recent first. An unfeatured event still reaches the talks list and the
    CV, so unmarking hides it from the homepage, never from the record."""
    picked = [e for e in data["events"]
              if e.get("visibility") == "public" and e.get("featured")]
    soon = sorted((e for e in picked if is_upcoming(e.get("date"))), key=lambda e: ym(e["date"]))
    past = sorted((e for e in picked if not is_upcoming(e.get("date"))),
                  key=lambda e: ym(e["date"]), reverse=True)
    rows = []
    for e in soon + past:
        rows.append({
            "when": data["strings"][lang]["news_soon"] if e in soon else fmt_date(e["date"], lang),
            "soon": e in soon,
            "name": field(e, "name", lang),
            "subtitle": e.get("subtitle", ""),
            "place": field(e, "place", lang),
            "host": e.get("host", ""),
            "role": data["strings"][lang]["roles"].get(e["role"], e["role"]),
            "title": t(e.get("title"), lang),
        })
    return rows


def authors_html(pub, person, conjunction="and"):
    """Reference-list author string, the author himself in bold, ending in a
    single period — the names already end in one, so the caller adds none."""
    names = [f"<strong>{a}</strong>" if a in person["cite_names"] else a
             for a in pub["authors"]]
    joined = f"{', '.join(names[:-1])} {conjunction} {names[-1]}" if len(names) > 1 else names[0]
    return joined if joined.endswith(".") else joined + "."


def research_lines(data, lang, status):
    lines = []
    for r in sorted((x for x in data["research"] if x["status"] == status),
                    key=lambda x: x.get("order", 99)):
        lines.append({
            "id": r["id"],
            "title": t(r["title"], lang),
            "collaborators": ", ".join(r.get("collaborators", [])),
            "prose": content(f"research/{r['id']}", lang),
            "publications": [p for p in data["publications"] if p.get("line") == r["id"]],
        })
    return lines


def talks(data, lang):
    rows = [{"year": ym(e["date"])[0],
             "kind": data["strings"][lang]["roles"][e["role"]],
             "title": t(e.get("title"), lang),
             "event": field(e, "name", lang),
             "place": field(e, "place", lang)}
            for e in data["events"]
            if e["visibility"] == "public" and e["role"] in ("oral", "poster")]
    return sorted(rows, key=lambda r: -r["year"])
