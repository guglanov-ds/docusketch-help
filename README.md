# DocuSketch mobile — help articles

How-to guides for the DocuSketch mobile app, published as a static site on
GitHub Pages. **Screenshots are never taken by hand** — every figure is composed
from the app's screenshot-test baselines, so the images always match the
shipped UI.

Live URL scheme (stable): `…/docs/how-to-<slug>/` — matches the existing help
center so links survive the migration. Today on GitHub Pages:
`https://guglanov-ds.github.io/docusketch-help/docs/how-to-add-a-timeline/`;
after the `help.docusketch.com` custom domain is attached (DNS CNAME →
`guglanov-ds.github.io` + a `CNAME` file), the same path serves at
`https://help.docusketch.com/docs/how-to-add-a-timeline`.

## How it works

```
docusketch-mobile screenshot tests  ──►  KMP/Screenshots/ios26/<module>/*.png
        (baseline PNGs)                            │
                                                   │  tools/pull-screens.sh
                                                   ▼
                                        docs/assets/raw/*.png
                                                   │  tools/compose.py + figures/*.yml
                                                   ▼
                                        docs/assets/<slug>/hero.png   (composites)
                                                   │  MkDocs Material
                                                   ▼
                                        static site  ──►  GitHub Pages
```

- **Baselines** come from the screenshot pipeline in `docusketch-mobile`
  (`KMP/docs/guides/screenshot-testing.md`). A state that doesn't exist yet is
  added as a `@ScreenshotTest`, then `./gradlew :testfoundation:screenshot-test-umbrella:verifyIosScreenshotsIos26 -PtestFilter=…` writes the PNG.
- **Bottom sheets** render realistically via `BottomSheetScreenshotFrame`
  (`:testfoundation:presentationfixture`) — a dimmed background, a bottom-pinned
  rounded surface — instead of full-screen.
- **`tools/compose.py`** lays 2–4 frames in a row with red highlight boxes,
  arrows and step badges in the design-system style. Layout is data
  (`figures/<slug>.yml`), so re-running is one command.

## Quick start

```bash
make setup     # venv + deps (mkdocs-material, Pillow, PyYAML)
make screens   # copy the needed baselines from the mobile worktree
make figures   # build every composite from figures/*.yml
make serve     # preview at http://127.0.0.1:8000/docusketch-help/
```

`make screens` reads from `$HOME/Developer/docusketch-mobile-help-screens` by
default; override with `make screens MOBILE=/path/to/worktree`.

## Add an article

1. If a step needs a screen state that has no baseline yet, add a
   `@ScreenshotTest` in the mobile repo and regenerate (see above).
2. Add the baseline → stable name mapping in `tools/pull-screens.sh`.
3. Add a composite spec to `figures/<slug>.yml` (frames, highlight boxes as
   fractions of the frame, optional `crop` for tall screens).
4. Write `docs/<slug>.md` and add it to `nav:` in `mkdocs.yml`.
5. `make figures && make serve`.

## Publish

GitHub Pages deploy is wired in `.github/workflows/pages.yml` (push to `main`)
and `make deploy` (`mkdocs gh-deploy`). **Run only when explicitly approved** —
the repo is local until then.
