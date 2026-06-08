# DocuSketch mobile — help articles

How-to guides for the DocuSketch mobile app, published as a static MkDocs site on GitHub
Pages. **Screenshots are never taken by hand** — every figure is composed from the app's
screenshot-test baselines (deterministic, mock data), so the images always match the shipped
UI.

Live: https://guglanov-ds.github.io/docusketch-help/ . URL scheme is the canonical
help-center slug — `/docs/<slug>/` — so links survive a future move to `help.docusketch.com`
(attach a CNAME + a `CNAME` file; no Actions workflow exists, deploy is `make deploy`).

## How it works

```
docusketch-mobile screenshot tests ─► KMP/Screenshots/ios26/<module>/*.png   (baseline PNGs)
                                            │  tools/pull-screens.sh
                                            ▼
                                   docs/assets/raw/*.png
                                            │  tools/compose.py + figures/<slug>.yml
                                            ▼
                          docs/assets/<slug>/NN-*.png   (composites)
                                            │  MkDocs Material
                                            ▼
                                   static site ─► GitHub Pages
```

**Composites are clean, native-looking iPhone 17 screens** (no callout boxes / arrows /
badges):
- The screenshot-test **baseline already contains the real native UIKit nav bar** (the
  harness wraps the Compose body in a `UINavigationController`). It does NOT contain the
  status bar (collapsed) or the tab bar (never instantiated).
- `tools/compose.py` adds the **real native status bar + tab bar**, captured once from the
  running app and cropped with `tools/crop-chrome.py` into `docs/assets/chrome/`
  (`status-bar-light-src.png`, `tab-bar-projects-src.png`, `tab-bar-camera-src.png`; the
  Dynamic Island is painted out).
- `build_device_frame` composes every frame onto a fixed **iPhone 17 aspect (1206:2622)** so
  all phones are the same shape: status bar on top, body at natural scale (tall scrollable
  screens are cropped to the top like a real phone; screen-height bodies get a sub-5% fit so
  bottom buttons aren't cut), floating tab bar overlaid at the bottom (`tabbar: projects` or
  `camera`).
- Backdrop is `#F9F9F5` (`--bg-neutral-light` from the design system).

## Quick start

```bash
make setup     # venv + deps (mkdocs-material, Pillow, PyYAML)
make screens   # copy the needed baselines from the mobile worktree
make figures   # build every composite from figures/*.yml
make serve     # preview at http://127.0.0.1:8000/docusketch-help/
```

`make screens` reads `$HOME/Developer/docusketch-mobile-help-screens` by default; override
with `make screens MOBILE=/path/to/worktree`.

## Add an article

A Document360 export goes in `tut<N>/` (gitignored — third-party/source). Then:

1. `python tools/extract-article.py tut<N>` → prints the canonical **slug**, **title**,
   verbatim **body** (markdown skeleton), **links**, and the **image list**.
2. Map each original frame to a screenshot-test baseline. If a screen has no baseline, either
   add a `@ScreenshotTest` in the mobile repo and regenerate (see below), or capture it live
   (see below). Add the `baseline → stable-name` copies to `tools/pull-screens.sh`, then
   `make screens`.
3. Write `figures/<slug>.yml` — one composite per original image; each frame is
   `{img: raw/<name>.png, tabbar: projects|camera}` (omit `tabbar` for modals/sheets).
   Defaults: `bg: "#F9F9F5"`, `status_bar: true`.
4. Write `docs/docs/<slug>.md` — text **verbatim** from the original, with UI-accurate wording
   where the app changed (e.g. "tap **View rooms**" where the original said "Rooms", mobile
   "tap" not "click").
5. Wire up: add to `nav:` in `mkdocs.yml`, a bullet in `docs/index.md`, and `tut<N>/` to
   `.gitignore`.
6. `make figures` → review the PNGs → `mkdocs build --strict`.

## New screen states

Most app screens already have an iOS-26 baseline (project list/overview, room list/detail,
camera connected/storage-low, sketch request, timeline room list, 360 viewer, alerts).

- **No baseline yet:** add a `@ScreenshotTest` in the mobile repo, then
  `./gradlew :testfoundation:screenshot-test-umbrella:verifyIosScreenshotsIos26 -PtestFilter=screenshots/<Class>IOS26`
  writes the PNG (a missing baseline is written, not failed; `xcodebuild` exit 65 is normal).
  Bottom sheets/alerts render realistically via `BottomSheetScreenshotFrame` /
  inline-approximation tests in `:testfoundation:presentationfixture`.
- **Driving the live app (idb on macOS 26):** `brew install idb-companion` is blocked by the
  outdated Command Line Tools, but the cached bottle works — extract
  `~/Library/Caches/Homebrew/downloads/*idb-companion.universal.tar.gz` and run
  `idb_companion --udid <booted-UDID> --grpc-port 10882` directly, then `idb connect localhost
  10882` + `idb ui tap/describe-all`. Capture with `xcrun simctl io booted screenshot`. (Login
  to the app is manual — credentials are never entered programmatically.)

## Publish

`make deploy` (`mkdocs gh-deploy --force`) builds and pushes to the `gh-pages` branch; Pages
serves it (the repo is public). Verify the live page + images return 200.
