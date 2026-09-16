#!/usr/bin/env python3
"""Derives assets/ from the untouched originals in ../Pics/.

The crop is a recipe, not a one-off file: re-running this reproduces exactly the
image on the site, and nobody has to remember what "the good crop" was.
Requires ImageMagick (convert), which is already installed."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PICS = ROOT.parent / "Pics"

RECIPES = {
    # Homepage portrait: the upper third dropped, lower two thirds kept, no retouching.
    "photo.jpg": {
        "src": "Personal_Photo_1.jpg",
        "crop": "1080x900+0+450",
        "width": 760,
        "quality": 82,
    },
    # Research page: explaining his poster at FoCM 2026, Vienna. The whole frame,
    # uncropped — it sits at the width of the text column, so it does not need to
    # be tightened. 1200px is twice that width, for high-density screens.
    "poster-focm.jpg": {
        "src": "Poster_FOCM.jpg",
        "width": 1200,
        "quality": 82,
    },
}


def build():
    (ROOT / "assets").mkdir(exist_ok=True)
    for name, r in RECIPES.items():
        src = PICS / r["src"]
        if not src.exists():
            sys.exit(f"missing original: {src}")
        cmd = ["convert", str(src)]
        if r.get("crop"):
            cmd += ["-crop", r["crop"], "+repage"]
        if r.get("width"):
            cmd += ["-resize", f"{r['width']}x"]
        cmd += ["-quality", str(r.get("quality", 85)), str(ROOT / "assets" / name)]
        subprocess.run(cmd, check=True)
        print(f"  assets/{name}  <- Pics/{r['src']}")


if __name__ == "__main__":
    print("deriving images:")
    build()
