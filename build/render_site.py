#!/usr/bin/env python3
"""data/ + content/ -> docs/.  Never hand-edit docs/: this file owns it."""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import model                                      # noqa: E402
import motif                                      # noqa: E402
from jinja2 import Environment, FileSystemLoader, StrictUndefined  # noqa: E402

ROOT = model.ROOT
OUT = ROOT / "docs"
# Pages that actually exist. Nav links to anything else resolve to "#" rather
# than to a 404 — add a name here the moment its template lands.
BUILT = {"home", "research", "publications"}
# Where each page is written, relative to docs/. English at the root, Spanish
# under /es/ — the user site sits at the domain root, so links are root-relative
# and a page at any depth keeps working.
PAGES = ["home", "research", "publications"]


def path_for(page, lang):
    parts = ([] if lang == "en" else ["es"]) + ([] if page == "home" else [page])
    return "/" + "/".join(parts) + ("/" if parts else "")


def url_for(lang):
    def url(page):
        return path_for(page, lang) if page in BUILT else "#"
    return url


def context_for(page, data, lang, s):
    """Everything a page needs, and nothing a page does not."""
    if page == "home":
        person = data["person"]
        return dict(
            bio=model.content("bio", lang),
            news=model.news(data, lang),
            publications=[{**p, "title": model.t(p["title"], lang),
                           "authors": model.authors_html(p, person, s["and"])}
                          for p in data["publications"]])
    if page == "research":
        return dict(active=model.research_lines(data, lang, "active"),
                    past=model.research_lines(data, lang, "past"))
    if page == "publications":
        person = data["person"]
        return dict(
            publications=[{**p, "title": model.t(p["title"], lang),
                           "authors": model.authors_html(p, person, s["and"])}
                          for p in data["publications"]],
            talks=model.talks(data, lang))
    raise ValueError(page)


TITLES = {"home": None,
          "research": "research_heading",
          "publications": "nav.publications"}


def render():
    data = model.load()
    env = Environment(loader=FileSystemLoader(ROOT / "site/templates"),
                      undefined=StrictUndefined, autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    person = data["person"]
    mark = motif.svg(size=30)
    full_name = f"{person['name']['first']} {person['name']['last']}"

    for lang in model.LANGS:
        s = data["strings"][lang]
        for page in PAGES:
            key = TITLES[page]
            heading = (s["nav"]["publications"] if key == "nav.publications"
                       else s[key]) if key else None
            html = env.get_template(f"{page}.html.j2").render(
                lang=lang, s=s, person=person, page=page, motif=mark,
                url=url_for(lang),
                home_url=path_for("home", lang),
                other_lang_url=path_for(page, "es" if lang == "en" else "en"),
                page_title=full_name if not heading else f"{heading} — {full_name}",
                page_description=model.t(person["tagline"], lang),
                **context_for(page, data, lang, s))
            target = OUT / path_for(page, lang).lstrip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print(f"  {target.relative_to(ROOT)}")

    # A page that stops being built must stop being served. docs/ is generated,
    # so nothing here is precious: drop any directory this run did not write.
    keep = {OUT} | {OUT / path_for(page, lang).lstrip("/")
                    for page in PAGES for lang in model.LANGS}
    for stale in sorted((d for d in OUT.rglob("*") if d.is_dir() and d not in keep),
                        reverse=True):
        shutil.rmtree(stale)
        print(f"  removed {stale.relative_to(ROOT)}/ — no longer a page")

    (OUT / "favicon.svg").write_text(motif.document(), encoding="utf-8")
    shutil.copy(ROOT / "site/static/style.css", OUT / "style.css")
    for name in ("photo.jpg", "poster-focm.jpg"):
        src = ROOT / "assets" / name
        if src.exists():
            shutil.copy(src, OUT / name)
        else:
            print(f"  ! assets/{name} missing — run: make images")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("  docs/style.css, docs/favicon.svg, images")


if __name__ == "__main__":
    print("rendering site:")
    render()
