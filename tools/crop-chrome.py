#!/usr/bin/env python3
"""Crop real native iOS chrome strips (status bar, tab bar) from a full-screen
simulator screenshot, for use by tools/compose.py.

The iOS screenshot-test baselines render the real native nav bar but collapse the
status bar (negative safe-area inset) and omit the tab bar (no UITabBarController in
the test host). So we capture those two bars once from the running app and let
compose.py splice them onto the deterministic Compose bodies.

Capture needs only a screenshot (no idb / no accessibility access):
    xcrun simctl io booted screenshot /tmp/full.png      # on a logged-in main screen

Crop coordinates are for iPhone 17 Pro, iOS 26 (1206x2622, @3x):
    status bar = top 177 px  (the 59pt safe-area top, above the native nav bar)
    tab bar    = bottom 240 px (the floating Liquid-Glass pill + margins)
compose.py width-matches each strip to the frame, so exact heights are not critical.

Usage:
    python tools/crop-chrome.py /tmp/full.png status docs/assets/chrome/status-bar-light-src.png
    python tools/crop-chrome.py /tmp/full.png tabbar docs/assets/chrome/tab-bar-projects-src.png
    # for the Camera-selected tab bar, capture on the Camera tab, then:
    python tools/crop-chrome.py /tmp/cam.png  tabbar docs/assets/chrome/tab-bar-camera-src.png
"""
from __future__ import annotations

import sys

from PIL import Image

STATUS_H = 177   # iPhone 17 Pro @3x — safe-area top (status bar only, no nav bar)
TABBAR_H = 240   # floating tab-bar pill + side margins + home-indicator area


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("status", "tabbar"):
        print(__doc__)
        return 2
    src, band, out = argv
    im = Image.open(src).convert("RGB")
    w, h = im.size
    crop = im.crop((0, 0, w, STATUS_H)) if band == "status" else im.crop((0, h - TABBAR_H, w, h))
    crop.save(out)
    print(f"wrote {out}  ({crop.size[0]}x{crop.size[1]})  [{band} band of {w}x{h}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
