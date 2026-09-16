#!/usr/bin/env python3
"""Compares the CVUy snapshot with data/ and writes reports/cvuy-drift.md.

The report is a to-do list in two directions: what to type into ANII by hand,
and what to add here. Run it before a llamado or a renovación. Nothing in this
file writes to data/ — reconciliation is a human decision every time."""
import difflib
import pathlib
import sys
import unicodedata

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import model                                      # noqa: E402

ROOT = model.ROOT
EVENT_SECTIONS = {"Participación en eventos", "Formación Complementaria"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(c for c in s if c.isalnum() or c.isspace()).strip()


def close(a, b, cutoff=0.82):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio() >= cutoff


def main():
    snap_path = ROOT / "data/_cvuy_snapshot.yml"
    if not snap_path.exists():
        sys.exit("no snapshot — run: make import-cvuy")
    snap = yaml.safe_load(snap_path.read_text(encoding="utf-8"))
    data = model.load()

    cvuy_events = [i for i in snap["items"] if i["section"] in EVENT_SECTIONS]
    ours = [e for e in data["events"] if e["visibility"] == "public"]

    missing_here, missing_there = [], []
    for c in cvuy_events:
        if not any(close(c["title"], model.field(e, "name", "es")) or
                   close(c["title"], model.field(e, "name", "en")) for e in ours):
            missing_here.append(c)
    for e in ours:
        names = [model.field(e, "name", "en"), model.field(e, "name", "es")]
        if not any(close(c["title"], n) for c in cvuy_events for n in names):
            missing_there.append(e)

    our_courses = {model.t(c["name"], "es") for c in data["teaching"]}
    cvuy_courses = {c["name"] for c in snap["courses"]}
    courses_missing_here = [c for c in cvuy_courses
                            if not any(close(c, o) for o in our_courses)]
    courses_missing_there = [c for c in our_courses
                             if not any(close(c, o) for o in cvuy_courses)]

    lines = [
        "# CVUy drift report", "",
        f"Snapshot: `{snap['source']}` · data/ as of this run.", "",
        "CVUy cannot be written to programmatically. Everything under "
        "*Type into ANII* is manual data entry at cvuy.anii.org.uy.", "",
        "Matching is fuzzy and bilingual: an entry can appear below simply "
        "because its Spanish name is missing here. Adding `name_es` clears it.", "",
        "## Defects inside CVUy itself", "",
    ]
    lines += [f"- {d}" for d in snap["defects"]] or ["- none detected"]
    lines += ["", "## Type into ANII — here but not in CVUy", ""]
    lines += [f"- **{model.field(e, 'name', 'es')}** ({e['date']}, {e['role']})"
              for e in missing_there] or ["- nothing"]
    lines += ["", "## Add to data/ — in CVUy but not here", ""]
    lines += [f"- **{c['title']}** ({c['year']}) — CVUy section: {c['section']}"
              for c in missing_here] or ["- nothing"]
    lines += ["", "## Courses", "",
              "In CVUy, not in teaching.yml:", ""]
    lines += [f"- {c}" for c in sorted(courses_missing_here)] or ["- nothing"]
    lines += ["", "In teaching.yml, not in CVUy:", ""]
    lines += [f"- {c}" for c in sorted(courses_missing_there)] or ["- nothing"]

    (ROOT / "reports").mkdir(exist_ok=True)
    out = ROOT / "reports/cvuy-drift.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}: {len(missing_there)} to type into ANII, "
          f"{len(missing_here)} to add here, "
          f"{len(courses_missing_here) + len(courses_missing_there)} course differences")


if __name__ == "__main__":
    main()
