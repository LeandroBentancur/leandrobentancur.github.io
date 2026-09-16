#!/usr/bin/env python3
"""data/ + content/ -> docs/.  Never hand-edit docs/: this file owns it."""
import datetime
import json
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
# Directories under docs/ that are not pages. The prune step below would
# otherwise delete them as stale on every build and copy them straight back.
STATIC_DIRS = {"fonts"}


def path_for(page, lang):
    parts = ([] if lang == "en" else ["es"]) + ([] if page == "home" else [page])
    return "/" + "/".join(parts) + ("/" if parts else "")


def url_for(lang):
    def url(page):
        return path_for(page, lang) if page in BUILT else "#"
    return url


def schema(data, lang, site_url):
    """A schema.org Person for the homepage.

    The pages already say who he is in prose; this says it in the form a search
    engine can act on, and — through sameAs — lets it join this page to the
    Scholar profile, the GitHub account and the ANII record as one person rather
    than four strangers who share a name. Built from data/, like everything
    else: nothing here is a fact that is not already written down once."""
    person, inst = data["person"], data["institutions"]
    links = person["links"]
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": f"{person['name']['first']} {person['name']['last']}",
        "givenName": person["name"]["first"],
        "familyName": person["name"]["last"],
        "jobTitle": model.t(person["role"], lang),
        "description": model.t(person["tagline"], lang),
        "url": site_url + "/",
        "image": f"{site_url}/photo.jpg",
        "email": f"mailto:{person['emails']['institutional']}",
        "affiliation": {
            "@type": "CollegeOrUniversity",
            "name": model.t(person["affiliation"], lang),
            "alternateName": "Udelar",
            "url": "https://www.cmat.edu.uy/",
        },
        "alumniOf": [{"@type": "CollegeOrUniversity",
                      "name": e["institution"]} for e in data["education"]
                     if e["id"] == "msc"],
        "knowsAbout": [model.t(r["title"], lang) for r in data["research"]
                       if r["status"] == "active"],
        "sameAs": [links[k] for k in ("scholar", "github", "arxiv", "cvuy", "cmat")
                   if links.get(k)],
    }
    # A literal </script> inside the block would end the tag early; escaping the
    # angle bracket is the standard defence and stays valid JSON.
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("<", "\\u003c")


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
    site_url = person["site_url"].rstrip("/")

    def absolute(page, lang):
        """The real https:// address of a page. Search engines need it spelled
        out — a root-relative path cannot say which of the two languages a page
        is, nor which one is the same page in the other language."""
        return site_url + path_for(page, lang)

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
                page_title=(f"{full_name} - {s['home_title_suffix']}" if not heading
                            else f"{heading} — {full_name}"),
                # The homepage's tagline already is its one-sentence summary;
                # the inner pages get their own, or they all look identical in
                # a search result and in a link preview.
                page_description=s["descriptions"][page],
                jsonld=(schema(data, lang, site_url) if page == "home" else ""),
                site_url=site_url,
                canonical=absolute(page, lang),
                alternates={l: absolute(page, l) for l in model.LANGS},
                **context_for(page, data, lang, s))
            target = OUT / path_for(page, lang).lstrip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            print(f"  {target.relative_to(ROOT)}")

    # A page that stops being built must stop being served. docs/ is generated,
    # so nothing here is precious: drop any directory this run did not write.
    keep = {OUT} | {OUT / d for d in STATIC_DIRS} | {
        OUT / path_for(page, lang).lstrip("/")
        for page in PAGES for lang in model.LANGS}
    for stale in sorted((d for d in OUT.rglob("*") if d.is_dir() and d not in keep),
                        reverse=True):
        shutil.rmtree(stale)
        print(f"  removed {stale.relative_to(ROOT)}/ — no longer a page")

    (OUT / "favicon.svg").write_text(motif.document(), encoding="utf-8")
    shutil.copy(ROOT / "site/static/style.css", OUT / "style.css")
    # The typeface is served from this origin, so it ships with the site.
    shutil.copytree(ROOT / "site/static/fonts", OUT / "fonts", dirs_exist_ok=True)
    for name in ("photo.jpg", "poster-focm.jpg"):
        src = ROOT / "assets" / name
        if src.exists():
            shutil.copy(src, OUT / name)
        else:
            print(f"  ! assets/{name} missing — run: make images")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # lastmod is the newest hand-edited source, not the moment of the build —
    # rebuilding without changing anything should not claim the page is new.
    newest = max(p.stat().st_mtime for d in ("data", "content", "site")
                 for p in (ROOT / d).rglob("*") if p.is_file())
    stamp = datetime.date.fromtimestamp(newest).isoformat()
    urls = []
    for page in PAGES:
        for lang in model.LANGS:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{l}" '
                f'href="{site_url + path_for(page, l)}"/>' for l in model.LANGS)
            urls.append(f"  <url>\n    <loc>{site_url + path_for(page, lang)}</loc>"
                        f"{alts}\n    <lastmod>{stamp}</lastmod>\n  </url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8")
    print("  docs/style.css, docs/favicon.svg, images, sitemap.xml, robots.txt")


if __name__ == "__main__":
    print("rendering site:")
    render()
