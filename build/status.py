#!/usr/bin/env python3
"""What is complete, what is seeded, what is still pending. Run it when you come
back to this repo after three months and need to know where you left off."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import model                                      # noqa: E402
import validate                                   # noqa: E402

PAGES = {"home": True, "research": True, "publications": True, "teaching": True}


def main():
    data = model.load()
    print("data")
    for name in sorted(k for k in data if k not in ("strings", "person")):
        node = data[name]
        n = len(node) if hasattr(node, "__len__") else 1
        print(f"  {name:16} {n:>3} entries" + ("   EMPTY" if not n else ""))
    print("\npages")
    for page, built in PAGES.items():
        print(f"  {page:16} {'built (en + es)' if built else 'not built — nav links to #'}")
    cv = model.ROOT.parent / "cv-build"
    print("\nCVs (outside this repo, in ../cv-build)")
    if not cv.exists():
        print("  cv-build         not found — the CVs are built from a sibling folder")
    for prof in sorted((cv / "profiles").glob("*.yml")) if cv.exists() else []:
        pdf = cv / f"out/{prof.stem}.pdf"
        print(f"  {prof.stem:16} {'built' if pdf.exists() else 'not built — cd ../cv-build && make'}")
    validate.check(data)
    print(f"\nvalidation: {len(validate.errors)} errors, {len(validate.warnings)} warnings")
    for w in validate.warnings:
        print(f"  warn   {w}")
    for e in validate.errors:
        print(f"  ERROR  {e}")


if __name__ == "__main__":
    main()
