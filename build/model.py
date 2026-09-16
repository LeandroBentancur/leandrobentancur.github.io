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


def news(data, lang, limit=6):
    """Public events only. Upcoming first, marked; then the most recent."""
    pub = [e for e in data["events"] if e.get("visibility") == "public"]
    soon = sorted((e for e in pub if is_upcoming(e.get("date"))), key=lambda e: ym(e["date"]))
    past = sorted((e for e in pub if not is_upcoming(e.get("date"))),
                  key=lambda e: ym(e["date"]), reverse=True)
    rows = []
    for e in soon + past[: max(0, limit - len(soon))]:
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


def attended(data, lang):
    rows = [{"year": ym(e["date"])[0],
             "name": field(e, "name", lang),
             "place": field(e, "place", lang),
             # organising implies attending, so it stays in this list, marked
             "role": data["strings"][lang]["roles"][e["role"]] if e["role"] == "organizer" else ""}
            for e in data["events"]
            if e["visibility"] == "public" and e["role"] not in ("oral", "poster", "visit")]
    return sorted(rows, key=lambda r: -r["year"])


def courses_by_institution(data, lang):
    """Courses grouped by where they were taught, most recent first."""
    groups = {}
    for course in data["teaching"]:
        for off in course["offerings"]:
            g = groups.setdefault(off["institution"], {})
            entry = g.setdefault(course["id"], {
                "name": t(course["name"], lang),
                "public_title": t(course.get("public_title"), lang),
                "years": set()})
            entry["years"].add(off["year"])
    out = []
    for inst_id, courses in groups.items():
        inst = data["institutions"][inst_id]
        rows = sorted(courses.values(), key=lambda c: -max(c["years"]))
        for r in rows:
            r["years"] = ", ".join(str(y) for y in sorted(r["years"], reverse=True))
        out.append({"institution": f"{t(inst['name'], lang)}, {t(inst['faculty'], lang)}"
                    if inst.get("faculty") else t(inst["name"], lang),
                    "courses": rows,
                    "latest": max(max(int(y) for y in c["years"].split(", ")) for c in rows)})
    return sorted(out, key=lambda g: -g["latest"])


def positions(data, lang):
    rows = []
    for p in data["positions"]:
        inst = data["institutions"][p["institution"]]
        end = str(p["end"])[:4] if p["end"] else data["strings"][lang]["present"]
        rows.append({"span": f"{str(p['start'])[:4]}–{end}",
                     "role": t(p["role"], lang),
                     "institution": t(inst["name"], lang) + (
                         f", {t(inst['faculty'], lang)}" if inst.get("faculty") else ""),
                     "project": p.get("project", "")})
    return rows


def current_course(data, lang):
    """The course with the most recent offering — the one the bio mentions."""
    best, best_year = None, -1
    for course in data["teaching"]:
        for off in course["offerings"]:
            if off["year"] > best_year:
                best, best_year = course, off["year"]
    return t(best["name"], lang) if best else ""
