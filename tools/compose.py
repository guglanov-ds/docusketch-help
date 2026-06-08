#!/usr/bin/env python3
"""Compose help-article figures from screenshot-test baseline PNGs.

Input  : a YAML spec describing one or more composites, each built from 2-4
         screenshot PNGs.
Output : one flat PNG per composite in the house style — light backdrop, phone
         frames in a row (rounded, soft shadow), red highlight boxes, red arrows
         between frames, numbered step badges.

No network, deterministic. Style values come from the DocuSketch design system
(backdrop --bg-neutral-light #F9F9F5, callout red --bg-error #E92F2F, text
--text-black #1A1905).

Usage:
    python tools/compose.py figures/connect-the-camera.yml [more.yml ...]
    python tools/compose.py figures/*.yml

Paths inside a spec (`img`, `out`) are resolved against docs/assets/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --- house style (design-system tokens) ------------------------------------

BG = "#F9F9F5"          # --bg-neutral-light
ACCENT = "#E92F2F"      # --bg-error / --text-error (callouts, arrows)
INK = "#1A1905"         # --text-black (captions)
FRAME_BORDER = "#E2E0D3"  # --stroke-neutral-default (hairline around frame)
SHADOW = (26, 25, 5, 35)  # ash, soft (half-opacity)

DEFAULTS = {
    "frame_height": 1180,   # px each frame is scaled to
    "gap": 150,             # px between frames (arrow lives here)
    "margin": 90,           # px around the canvas
    "radius": 30,           # frame corner radius (px)
    "highlight_width": 9,   # red box stroke (px)
    "highlight_pad": 10,    # px the box sits outside the target
    "arrow_width": 12,
    "arrow_head": 46,
    "caption_size": 46,
    "badge_size": 78,
    "bg": BG,
    "accent": ACCENT,
}

ASSETS = Path(__file__).resolve().parent.parent / "docs" / "assets"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


CHROME_DIR = ASSETS / "chrome"


def _load_chrome(name: str) -> Image.Image | None:
    p = CHROME_DIR / name
    return Image.open(p).convert("RGB") if p.exists() else None


# Real native iOS 26 chrome captured from the running app (see tools/crop-chrome.py),
# keyed by variant. Old single-file names kept as fallbacks for back-compat.
_STATUS_BARS = {
    "light": _load_chrome("status-bar-light-src.png") or _load_chrome("status-bar-src.png"),
    "dark": _load_chrome("status-bar-dark-src.png"),
}
_TAB_BARS = {
    "projects": _load_chrome("tab-bar-projects-src.png") or _load_chrome("tab-bar-src.png"),
    "camera": _load_chrome("tab-bar-camera-src.png"),
}


def trim_trailing(img: Image.Image, tol: int = 12) -> Image.Image:
    """Drop uniform-colour trailing rows (blank space below content) — never chrome."""
    img = img.convert("RGB")
    w, h = img.size
    px = img.load()
    base = px[w // 2, h - 1]
    def uniform(y):
        return all(abs(px[x, y][i] - base[i]) <= tol for x in range(0, w, 8) for i in range(3))
    y = h - 1
    while y > h * 0.4 and uniform(y):
        y -= 1
    return img.crop((0, 0, w, min(h, y + 14)))


def add_chrome(src: Image.Image, status=None, tabbar=None) -> Image.Image:
    """Splice real native iOS chrome onto a screenshot-test baseline: a status bar on top
    and/or the app tab bar at the bottom. The nav bar is already real UIKit inside the
    baseline, so it is never added here. `status` is light|dark|True(=light)|None;
    `tabbar` is projects|camera|True(=projects)|None. Strips are width-matched to `src`."""
    w = src.width

    def _pick(v, default_key, table):
        if not v:
            return None
        img = table.get(default_key if v is True else str(v))
        return (img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
                if img is not None else None)

    sb = _pick(status, "light", _STATUS_BARS)
    tb = _pick(tabbar, "projects", _TAB_BARS)
    total = (sb.height if sb else 0) + src.height + (tb.height if tb else 0)
    canvas = Image.new("RGB", (w, total), "white")
    y = 0
    if sb is not None:
        canvas.paste(sb, (0, y)); y += sb.height
    canvas.paste(src, (0, y)); y += src.height
    if tb is not None:
        canvas.paste(tb, (0, y))
    return canvas


def rounded(img: Image.Image, radius: int) -> Image.Image:
    """Return img (RGBA) with rounded corners and a hairline border."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                           radius=radius, fill=255)
    img.putalpha(mask)
    border = ImageDraw.Draw(img)
    border.rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                             radius=radius, outline=FRAME_BORDER, width=2)
    return img


def with_shadow(card: Image.Image, radius: int, blur: int = 17,
                offset: tuple[int, int] = (0, 8)) -> tuple[Image.Image, int]:
    """Wrap a rounded RGBA card in a soft drop shadow. Returns (image, pad)."""
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    w, h = card.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [pad + offset[0], pad + offset[1], pad + offset[0] + w, pad + offset[1] + h],
        radius=radius, fill=SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(card, (pad, pad))
    return canvas, pad


def draw_arrow(draw: ImageDraw.ImageDraw, x0, y0, x1, y1, color, width, head):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)
    # horizontal arrowhead pointing toward (x1, y1)
    draw.polygon(
        [(x1, y1), (x1 - head, y1 - head * 0.55), (x1 - head, y1 + head * 0.55)],
        fill=color)


def draw_badge(draw: ImageDraw.ImageDraw, cx, cy, n, color, size, font):
    r = size // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    text = str(n)
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text((cx - tw / 2 - tb[0], cy - th / 2 - tb[1]), text, fill="white", font=font)


def compose_one(spec: dict, defaults: dict, out_root: Path) -> Path:
    d = {**DEFAULTS, **defaults, **{k: v for k, v in spec.items() if k in DEFAULTS}}
    fh, gap, margin, radius = d["frame_height"], d["gap"], d["margin"], d["radius"]
    accent = d["accent"]

    frames = spec["frames"]
    show_badges = spec.get("badges", True)   # set false for clean, annotation-free strips
    has_caption = any(f.get("caption") for f in frames)
    cap_font = load_font(d["caption_size"])
    badge_font = load_font(int(d["badge_size"] * 0.46))

    # Render each frame -> rounded card -> shadowed card; remember geometry.
    cards, pads, scaled_sizes = [], [], []
    for f in frames:
        src = Image.open(ASSETS / f["img"]).convert("RGB")
        if f.get("trim"):
            src = trim_trailing(src)
        crop = f.get("crop")  # keep top fraction of a tall screen (0..1)
        if crop:
            src = src.crop((0, 0, src.width, int(src.height * crop)))
        status_v = f.get("status_bar", d.get("status_bar"))  # frame overrides spec/defaults
        tabbar_v = f.get("tabbar")
        if status_v or tabbar_v:
            src = add_chrome(src, status=status_v, tabbar=tabbar_v)
        scale = fh / src.height
        sw = round(src.width * scale)
        scaled = src.resize((sw, fh), Image.LANCZOS)
        card, pad = with_shadow(rounded(scaled, radius), radius)
        cards.append(card)
        pads.append(pad)
        scaled_sizes.append((sw, fh))

    cap_h = d["caption_size"] + 36 if has_caption else 0
    card_h = cards[0].size[1]
    total_w = margin * 2 + sum(c.size[0] for c in cards) + gap * (len(cards) - 1)
    total_h = margin * 2 + card_h + cap_h

    canvas = Image.new("RGB", (total_w, total_h), d["bg"])
    draw = ImageDraw.Draw(canvas)

    inner_boxes = []  # (fx, fy, fw, fh) of each phone frame on the canvas
    x = margin
    for card, pad, (sw, sh) in zip(cards, pads, scaled_sizes):
        canvas.paste(card, (x, margin), card)
        inner_boxes.append((x + pad, margin + pad, sw, sh))
        x += card.size[0] + gap

    # Red highlight boxes (rounded outline) at relative coords on each frame.
    for (fx, fy, fw, fh_), f in zip(inner_boxes, frames):
        for hl in f.get("highlights", []):
            hp = d["highlight_pad"]
            bx0 = fx + hl["x"] * fw - hp
            by0 = fy + hl["y"] * fh_ - hp
            bx1 = fx + (hl["x"] + hl["w"]) * fw + hp
            by1 = fy + (hl["y"] + hl["h"]) * fh_ + hp
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=18,
                                   outline=accent, width=d["highlight_width"])

    # Arrows in the gaps between consecutive frames.
    if spec.get("arrows", True) and len(inner_boxes) > 1:
        for i in range(len(inner_boxes) - 1):
            lx, ly, lw, lh = inner_boxes[i]
            rx, ry, rw, rh = inner_boxes[i + 1]
            cy = margin + card_h // 2
            x0 = lx + lw + 12          # right edge of left frame
            x1 = rx - 12               # left edge of right frame
            draw_arrow(draw, x0, cy, x1, cy, accent, d["arrow_width"], d["arrow_head"])

    # Step badges (top-left of each frame) + captions (below).
    for idx, ((fx, fy, fw, fh_), f) in enumerate(zip(inner_boxes, frames), start=1):
        step = f.get("step", idx)
        if step and show_badges:
            bs = d["badge_size"] // 2
            draw_badge(draw, fx + bs, fy + bs, step, accent, d["badge_size"], badge_font)
        cap = f.get("caption")
        if cap:
            tb = draw.textbbox((0, 0), cap, font=cap_font)
            tw = tb[2] - tb[0]
            draw.text((fx + fw / 2 - tw / 2, margin + card_h + 18), cap,
                      fill=INK, font=cap_font)

    out_path = out_root / spec["out"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    for spec_file in argv:
        doc = yaml.safe_load(Path(spec_file).read_text())
        defaults = doc.get("defaults", {})
        for spec in doc.get("composites", []):
            try:
                out = compose_one(spec, defaults, ASSETS)
            except FileNotFoundError as e:
                print(f"skipped {spec.get('out')} (missing input: {getattr(e, 'filename', e)})")
                continue
            print(f"wrote {out.relative_to(ASSETS.parent.parent)}  ({Image.open(out).size[0]}x{Image.open(out).size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
