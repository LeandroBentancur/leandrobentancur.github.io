#!/usr/bin/env python3
"""CVUy (ANII) .txt export -> data/_cvuy_snapshot.yml (read-only).

CVUy is the most complete academic record Leandro has, but it is export-only:
no API, no import, data gets in by typing into ANII's web form. So it is never
an upstream of this build — it is a mirror to compare against. The snapshot this
writes is consumed by reconcile.py and by nothing else."""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT.parent / "CV/CVUY/CVUY_26_05_20.txt"
SECTIONS = ["Datos Generales", "Formación", "Formación Complementaria",
            "Participación en eventos", "Idiomas", "Áreas de Actuación",
            "Actuación Profesional", "Actividades", "Docencia", "Extensión",
            "Producción", "Producción científica", "Evaluaciones", "Formación RRHH"]
# A record head: a title carrying its year(s), e.g. "Escuela ... (2025)".
HEAD = re.compile(r"^(?P<title>.+?)\s*\((?P<years>\d{4}(?:\s*-\s*\d{4})?)\)\s*$")
COURSE = re.compile(r"^(?P<name>.+?),\s*(?P<hours>\d+)\s*horas?\s*$")


def parse(text):
    section = "?"
    items, courses = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in SECTIONS:
            section = line
            continue
        head = HEAD.match(line)
        if head:
            years = [int(y) for y in re.findall(r"\d{4}", head["years"])]
            items.append({"section": section, "title": head["title"].strip(),
                          "year": years[0], "year_end": years[-1] if len(years) > 1 else None})
            continue
        course = COURSE.match(line)
        if course:
            courses.append({"name": course["name"].strip(), "hours": int(course["hours"])})
    return items, courses


def defects(text):
    """Errors that live inside CVUy itself and can only be fixed at ANII."""
    found = []
    if "http://https://" in text:
        found.append("Sitio Web has a double scheme: http://https://www.cmat.edu.uy/...")
    if "Jerarquías poliedrales" in text:
        found.append("PhD thesis is still the dropped polyhedral-hierarchies title")
    return found


def main(src=None):
    src = pathlib.Path(src) if src else DEFAULT_SRC
    text = src.read_text(encoding="utf-8-sig")
    items, courses = parse(text)
    out = ROOT / "data/_cvuy_snapshot.yml"
    out.write_text(yaml.safe_dump({
        "source": str(src.name),
        "defects": defects(text),
        "items": items,
        "courses": courses,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}: {len(items)} items, {len(courses)} course lines")
    for d in defects(text):
        print(f"  defect at ANII: {d}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
