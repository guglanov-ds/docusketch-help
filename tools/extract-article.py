#!/usr/bin/env python3
"""Extract the essentials from a Document360 article export, for reproduction.

Usage:  python tools/extract-article.py <tut-dir>     (e.g. `tut4`, or a path)

Prints, for the single `.html` in <tut-dir>:
  - canonical SLUG (from <link rel=canonical> / og:url) -> file docs/docs/<slug>.md, URL /docs/<slug>/
  - H1 TITLE
  - LINKS (visible text -> href), minus Prev/Next/Follow chrome
  - BODY as a markdown skeleton (verbatim text, **bold**, ![](image) placeholders)
  - IMAGES (the PNGs in <tut-dir>/<name>_files/)

A starting point only — the screen->baseline mapping and any UI-accuracy wording tweaks
(e.g. "tap View rooms" where the original said "Rooms") are still done by hand.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_DROP = re.compile(r"Updated on|Published on|minute\(s\) read|^\s*(?:(?:Follow|Prev|Next|Login)\s*)+$")


def extract(path: Path) -> None:
    s = path.read_text(encoding="utf-8", errors="ignore")

    slug = ""
    for pat in (r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"',
                r'<meta[^>]+property="og:url"[^>]+content="([^"]+)"'):
        m = re.search(pat, s)
        if m:
            slug = m.group(1).rstrip("/").rsplit("/", 1)[-1]
            print(f"URL:   {m.group(1)}")
            break
    print(f"SLUG:  {slug}   ->  docs/docs/{slug}.md   ->  /docs/{slug}/")

    m = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S | re.I)
    print(f"TITLE: {html.unescape(re.sub('<[^>]+>', '', m.group(1)).strip()) if m else ''}\n")

    m = re.search(r'(<h1[^>]*>.*?)(<footer|</article>|<div[^>]*class="[^"]*article-footer)', s, re.S | re.I)
    chunk = m.group(1) if m else s

    print("--- LINKS ---")
    for href, txt in re.findall(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', chunk, re.S):
        t = html.unescape(re.sub("<[^>]+>", "", txt)).strip()
        if t and t not in ("Prev", "Next", "Follow", "Login"):
            print(f"  {t!r} -> {href}")

    print("\n--- BODY (markdown skeleton) ---")
    c = re.sub(r"</?(strong|b)>", "**", chunk)
    c = re.sub(r'<img[^>]*?src="([^"]*)"[^>]*>', lambda mm: f"\n![]({mm.group(1).split('/')[-1]})\n", c)
    c = re.sub(r"<li[^>]*>", "\n- ", c)
    c = re.sub(r"<h1[^>]*>", "\n# ", c)
    c = re.sub(r"<h[2-6][^>]*>", "\n\n## ", c)
    c = re.sub(r"<(p|div|br)[^>]*>", "\n", c)
    c = html.unescape(re.sub("<[^>]+>", "", c))
    c = re.sub(r"\n[ \t]+", "\n", c)
    c = re.sub(r"\n{3,}", "\n\n", c)
    print("\n".join(ln for ln in c.split("\n") if not _DROP.search(ln)).strip())

    files = path.parent / f"{path.stem}_files"
    print("\n--- IMAGES ---")
    if files.is_dir():
        for p in sorted(files.glob("*.png")):
            print(f"  {p.name}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    arg = Path(argv[0])
    d = arg if arg.is_dir() else ROOT / argv[0]
    htmls = sorted(d.glob("*.html")) if d.is_dir() else []
    if not htmls:
        print(f"no .html found in {d}")
        return 1
    extract(htmls[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
