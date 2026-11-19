#!/usr/bin/env python3
"""Build the public static site into build/site/.

  python3 tools/build_static.py
  TURNSTILE_SITEKEY=0x... python3 tools/build_static.py

The same frontend/index.html as ./serve.py, but with no local server behind it: the
problem data is pre-rendered to JSON, the learner's drafts, solutions and progress live in
the browser's localStorage, and Submit goes to POST /api/check/<id> on the Cloudflare
Worker (grader/worker/), which checks Turnstile and forwards to the cloud grader.

  build/site/index.html            the page, with window.STATIC_SITE set
  build/site/problems.json         the problem list
  build/site/p/<id>.json           README, starter code, reference solution
  build/site/p/<id>/diagram*.svg   the README's images

Starter code always comes from problems/<id>/starter/, so local work in problems/ never
leaks into the site. Reference solutions are public in the bundle; the page only shows
them once the problem has passed.

Preview without the grader: python3 -m http.server -d build/site
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check  # noqa: E402

OUT = check.BUILD / "site"
MARKER = "<script>\nconst $ ="     # the page's main script; the config goes just before it


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, separators=(",", ":")))


def main():
    sitekey = os.environ.get("TURNSTILE_SITEKEY", "")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    probs = check.load_problems()
    write_json(OUT / "problems.json", [
        {"id": p["id"], "section": p["section"], "num": p["num"], "name": p["name"],
         "section_title": check.SECTION_TITLES.get(p["section"], "")}
        for p in probs
    ])
    for p in probs:
        files = []
        for f in check.editable_files(p):
            starter = p["dir"] / "starter" / f.name
            if not starter.is_file():
                raise SystemExit(f"{p['id']}: no starter/{f.name}")
            files.append({"name": f.name, "starter": starter.read_text()})
        ref = check.SOLUTIONS / f"{p['id']}.vhd"
        write_json(OUT / "p" / f"{p['id']}.json", {
            "id": p["id"],
            "readme": (p["dir"] / "README.md").read_text(),
            "files": files,
            "reference": ref.read_text() if ref.is_file() else None,
        })
        for svg in p["dir"].iterdir():
            if re.fullmatch(r"diagram(_\d+)?\.svg", svg.name):
                (OUT / "p" / p["id"]).mkdir(exist_ok=True)
                shutil.copyfile(svg, OUT / "p" / p["id"] / svg.name)

    page = (check.ROOT / "frontend" / "index.html").read_text()
    if MARKER not in page:
        raise SystemExit("frontend/index.html: main script not found")
    config = f"<script>window.STATIC_SITE = {json.dumps({'turnstileSiteKey': sitekey})};</script>\n"
    (OUT / "index.html").write_text(page.replace(MARKER, config + MARKER, 1))

    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"{len(probs)} problems -> {OUT.relative_to(check.ROOT)} ({size / 1e6:.1f} MB)"
          + ("" if sitekey else "; no TURNSTILE_SITEKEY, so Submit sends no token"))


if __name__ == "__main__":
    main()
