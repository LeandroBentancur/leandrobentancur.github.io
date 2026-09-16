#!/usr/bin/env python3
"""The gate. Everything that can silently rot is checked here, and `make site`
refuses to run if it fails. Errors block; warnings are the to-do list."""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import model                                      # noqa: E402

errors, warnings = [], []


def check(data):
    people = data["person"]
    # --- identity ----------------------------------------------------------
    for key, addr in people["emails"].items():
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", addr):
            errors.append(f"person.emails.{key}: {addr!r} is not a valid address")
        if addr.endswith(".com.uy"):
            errors.append(f"person.emails.{key}: {addr!r} — the .com.uy typo is back")

    # --- events ------------------------------------------------------------
    ids = set()
    for e in data["events"]:
        where = f"events/{e.get('id', '?')}"
        if e["id"] in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(e["id"])
        if e.get("visibility") not in ("public", "private"):
            errors.append(f"{where}: visibility must be public or private")
        # A talk without a title is suspicious; a poster without one is fine —
        # the site never prints poster titles, and the CV degrades gracefully.
        if e["role"] == "oral" and not e.get("title"):
            warnings.append(f"{where}: talk with no title recorded")
        if not re.fullmatch(r"\d{4}(-\d{2})?", str(e.get("date", ""))):
            errors.append(f"{where}: date must be YYYY or YYYY-MM, got {e.get('date')!r}")
        if model.is_upcoming(e.get("date")) and e.get("visibility") == "public":
            warnings.append(f"{where}: upcoming AND public — confirm it is announced")
        if e.get("featured") and e.get("visibility") != "public":
            errors.append(f"{where}: featured but not public — the homepage would leak it")

    # --- publications ------------------------------------------------------
    for p in data["publications"]:
        where = f"publications/{p['id']}"
        if p["status"] == "published" and not all(p.get(k) for k in ("journal", "volume", "pages")):
            errors.append(f"{where}: published entry needs journal, volume and pages")
        if p["status"] == "preprint" and not p.get("arxiv"):
            warnings.append(f"{where}: preprint with no arXiv id")

    # --- teaching ----------------------------------------------------------
    known_inst = set(data["institutions"])
    for c in data["teaching"]:
        seen = set()
        for off in c["offerings"]:
            if off["institution"] not in known_inst:
                errors.append(f"teaching/{c['id']}: unknown institution {off['institution']!r}")
            key = (off["year"], off["institution"])
            if key in seen:
                errors.append(f"teaching/{c['id']}: {off['year']} listed twice")
            seen.add(key)

    # --- the things the audit found, which must not come back --------------
    phd = next((e for e in data["education"] if e["id"] == "phd"), None)
    if phd and "poliedral" in (phd.get("thesis") or "").lower():
        errors.append("education/phd: the dropped polyhedral-hierarchies title is back")

    # --- i18n mappings -----------------------------------------------------
    # A value written {es: text with, a comma, en: ...} parses as four keys and
    # silently loses half the text. This caught exactly that, twice.
    def walk(node, path):
        if isinstance(node, dict):
            keys = set(node)
            if keys & {"en", "es"} and not keys <= {"en", "es"}:
                stray = ", ".join(sorted(str(k) for k in keys - {"en", "es"}))
                errors.append(f"{path}: i18n mapping has stray keys ({stray}) — "
                              f"a comma inside a {{...}} value split it; quote it or use block style")
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    for name, node in data.items():
        if name != "strings":
            walk(node, name)

    # --- completeness ------------------------------------------------------
    # The homepage news list is hand-picked, so it is the one list that goes
    # quietly empty by neglect rather than by a change to the code.
    if not any(e.get("featured") for e in data["events"]):
        warnings.append("events.yml: nothing marked featured — the homepage news list is empty")
    for name in ("outreach", "service"):
        if not data[name]:
            warnings.append(f"{name}.yml: empty — still to be filled from the Spanish CV")
    if not people["links"]["cvuy"]:
        warnings.append("person.links.cvuy: empty — the nav CV link points nowhere")
    for lang in model.LANGS:
        missing = [r["id"] for r in data["research"]
                   if not (model.ROOT / f"content/research/{r['id']}.{lang}.md").exists()]
        if missing:
            warnings.append(f"content/research: missing {lang} prose for {', '.join(missing)}")


if __name__ == "__main__":
    check(model.load())
    for w in warnings:
        print(f"  warn   {w}")
    for e in errors:
        print(f"  ERROR  {e}")
    print(f"validate: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)
