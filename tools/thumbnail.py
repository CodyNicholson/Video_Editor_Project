#!/usr/bin/env python3
"""Compose thumbnails/covers with bold text, and preview them at real-world sizes.

Subcommands
-----------
compose   background (+ optional cut-out subject, logo) + auto-fitted headline
preview   legibility sheet: the thumbnail at feed / sidebar / phone sizes on
          dark + light UI, or safe-zone + grid-crop guides for vertical covers

Usage:
    .venv/bin/python tools/thumbnail.py compose --bg frame.jpg --size youtube \
        --text "I BUILT AN|*AI EDITOR*" --align left --out thumbnails/v1.jpg
    .venv/bin/python tools/thumbnail.py compose --bg ai_bg.png --subject me_cutout.png \
        --subject-side right --text "*3* SETTINGS|PROS USE" --accent "#FFD400" --out v2.jpg
    .venv/bin/python tools/thumbnail.py compose --bg frame.jpg --size vertical \
        --text "STOP DOING|*THIS*" --text-y 0.30 --out cover.jpg
    .venv/bin/python tools/thumbnail.py preview thumbnails/v1.jpg thumbnails/v2.jpg

Text syntax: "|" = line break, *word* = accent color.
Sizes: youtube 1280x720 | vertical 1080x1920 | feed 1080x1350 | square 1080x1080 |
       linkedin 1200x627 | x 1600x900
Fonts: name or file in brand/fonts (default Anton-Regular.ttf).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "brand" / "fonts"
SIZES = {"youtube": (1280, 720), "vertical": (1080, 1920), "feed": (1080, 1350),
         "square": (1080, 1080), "linkedin": (1200, 627), "x": (1600, 900)}


def font_path(name: str) -> Path:
    p = Path(name)
    if p.exists():
        return p
    cands = list(FONTS.glob(f"{name}*")) + list(FONTS.glob(f"*{name.replace(' ', '')}*"))
    cands = [c for c in cands if c.suffix.lower() in (".ttf", ".otf")]
    if not cands:
        raise SystemExit(f"font not found: {name} (look in {FONTS})")
    return sorted(cands, key=lambda c: len(c.name))[0]


def load_font(path: Path, size: int, weight: str | None):
    f = ImageFont.truetype(str(path), size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


def cover(img: Image.Image, W: int, H: int, focus_x: float, focus_y: float) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = int(min(max(focus_x * img.width - W / 2, 0), img.width - W))
    y = int(min(max(focus_y * img.height - H / 2, 0), img.height - H))
    return img.crop((x, y, x + W, y + H))


def parse_lines(text: str):
    lines = []
    for raw in text.split("|"):
        tokens = []
        for tok in re.findall(r"\*[^*]+\*|[^\s*]+", raw.strip()):
            tokens.append((tok.strip("*"), tok.startswith("*")))
        lines.append(tokens)
    return lines


def line_width(draw, tokens, font, space):
    return sum(draw.textlength(t, font=font) for t, _ in tokens) + space * (len(tokens) - 1)


def fit_font(draw, lines, fpath, weight, box_w, box_h, line_gap):
    lo, hi = 10, 600
    while lo < hi:
        mid = (lo + hi + 1) // 2
        f = load_font(fpath, mid, weight)
        sp = draw.textlength(" ", font=f)
        asc, desc = f.getmetrics()
        lh = asc + desc
        total_h = lh * len(lines) + int(lh * line_gap) * (len(lines) - 1)
        widest = max(line_width(draw, ln, f, sp) for ln in lines)
        if widest <= box_w and total_h <= box_h:
            lo = mid
        else:
            hi = mid - 1
    return load_font(fpath, lo, weight)


def compose(a):
    W, H = SIZES[a.size]
    bg = cover(Image.open(a.bg), W, H, a.focus_x, a.focus_y) if a.bg else Image.new("RGB", (W, H), a.bg_color)
    if a.saturate != 1.0:
        bg = ImageEnhance.Color(bg).enhance(a.saturate)
    if a.contrast != 1.0:
        bg = ImageEnhance.Contrast(bg).enhance(a.contrast)
    canvas = bg.convert("RGBA")

    # gradient scrim behind the text side for legibility
    if a.scrim > 0:
        scrim = Image.new("L", (W, H), 0)
        sd = ImageDraw.Draw(scrim)
        vertical = H > W
        for i in range(W if not vertical else H):
            frac = i / (W if not vertical else H)
            if vertical:
                d = abs(frac - a.text_y)
                val = int(255 * a.scrim * max(0.0, 1 - d / 0.35))
                sd.line([(0, i), (W, i)], fill=val)
            else:
                if a.align == "left":
                    val = int(255 * a.scrim * max(0.0, 1 - frac / 0.75))
                elif a.align == "right":
                    val = int(255 * a.scrim * max(0.0, (frac - 0.25) / 0.75))
                else:
                    val = int(255 * a.scrim * 0.6)
                sd.line([(i, 0), (i, H)], fill=val)
        canvas = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), canvas, scrim)

    # cut-out subject (PNG with alpha), with white outline + shadow
    if a.subject:
        subj = Image.open(a.subject).convert("RGBA")
        sh = int(H * a.subject_scale)
        subj = subj.resize((int(subj.width * sh / subj.height), sh), Image.LANCZOS)
        sx = W - subj.width + int(subj.width * 0.05) if a.subject_side == "right" else -int(subj.width * 0.05)
        if a.subject_side == "center":
            sx = (W - subj.width) // 2
        sy = H - subj.height
        alpha = subj.split()[-1]
        if a.subject_outline > 0:
            ring = alpha.filter(ImageFilter.MaxFilter(a.subject_outline * 2 + 1))
            canvas.paste(Image.new("RGBA", subj.size, a.outline_color), (sx, sy), ring)
        shadow = alpha.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.6))
        canvas.paste(Image.new("RGBA", subj.size, (0, 0, 0, 255)), (sx + 10, sy + 10), shadow)
        canvas.alpha_composite(subj, (sx, sy))

    # headline
    if a.text:
        draw = ImageDraw.Draw(canvas)
        lines = parse_lines(a.text.upper() if a.upper else a.text)
        fpath = font_path(a.font)
        margin = int(min(W, H) * 0.06)
        if H > W:  # vertical cover: centered block around text_y
            box_w, box_h = W - 2 * margin - int(W * 0.08), int(H * a.text_h)
        else:
            box_w = int(W * a.text_w) - margin
            box_h = H - 2 * margin
        f = fit_font(draw, lines, fpath, a.weight, box_w, box_h, a.line_gap)
        sp = draw.textlength(" ", font=f)
        asc, desc = f.getmetrics()
        lh = asc + desc
        gap = int(lh * a.line_gap)
        total_h = lh * len(lines) + gap * (len(lines) - 1)
        y = (int(H * a.text_y - total_h / 2) if H > W else (H - total_h) // 2)
        stroke = max(2, int(f.size * a.stroke))
        shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_layer)
        positions = []
        for ln in lines:
            lw = line_width(draw, ln, f, sp)
            if H > W or a.align == "center":
                x = (W - lw) / 2
            elif a.align == "left":
                x = margin
            else:
                x = W - margin - lw
            positions.append((x, y, ln))
            for tok, _ in ln:
                sdraw.text((x + f.size * 0.04, y + f.size * 0.05), tok, font=f, fill=(0, 0, 0, 200),
                           stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
                x += draw.textlength(tok, font=f) + sp
            y += lh + gap
        canvas.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(max(2, f.size // 18))))
        for x, y, ln in positions:
            for tok, accent in ln:
                draw.text((x, y), tok, font=f, fill=a.accent if accent else a.color,
                          stroke_width=stroke, stroke_fill=a.stroke_color)
                x += draw.textlength(tok, font=f) + sp

    if a.logo:
        logo = Image.open(a.logo).convert("RGBA")
        lw = int(W * 0.12)
        logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
        canvas.alpha_composite(logo, (W - lw - int(W * 0.03), int(H * 0.04)))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgb = canvas.convert("RGB")
    if out.suffix.lower() in (".jpg", ".jpeg"):
        q = 92
        rgb.save(out, quality=q, optimize=True)
        while out.stat().st_size > 1.9 * 1024 * 1024 and q > 60:  # YouTube limit: 2 MB
            q -= 6
            rgb.save(out, quality=q, optimize=True)
    else:
        rgb.save(out)
    print(f"wrote {out} ({W}x{H}, {out.stat().st_size // 1024} KB)")


def preview(a):
    ui_font = font_path("Inter")
    for p in a.images:
        img = Image.open(p).convert("RGB")
        stem = Path(p).with_suffix("")
        if img.height > img.width:  # vertical cover guides
            g = img.copy().convert("RGBA")
            ov = Image.new("RGBA", g.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            W, H = g.size
            d.rectangle([0, 0, W, int(H * 0.11)], fill=(255, 0, 0, 70))          # top UI
            d.rectangle([0, int(H * 0.77), W, H], fill=(255, 0, 0, 70))          # caption/UI
            d.rectangle([int(W * 0.86), int(H * 0.40), W, int(H * 0.77)], fill=(255, 0, 0, 70))  # action rail
            gh = int(W * 4 / 3)                                                   # IG profile grid 3:4
            d.rectangle([0, (H - gh) // 2, W - 1, (H + gh) // 2], outline=(0, 255, 120, 255), width=6)
            g = Image.alpha_composite(g, ov).convert("RGB")
            small = img.resize((W // 6, H // 6), Image.LANCZOS)
            sheet = Image.new("RGB", (W + small.width + 60, H), (24, 24, 24))
            sheet.paste(g, (0, 0)); sheet.paste(small, (W + 30, 30))
            out = Path(f"{stem}_preview.jpg"); sheet.save(out, quality=88)
            print(f"wrote {out}  (red = UI overlap zones, green = 3:4 profile-grid crop)")
            continue
        sizes = [(640, 360), (360, 202), (168, 94)]
        sheet = Image.new("RGB", (1400, 920), (15, 15, 15))
        d = ImageDraw.Draw(sheet)
        f = ImageFont.truetype(str(ui_font), 22)
        x = 30
        for i, (bgc, fg) in enumerate([((15, 15, 15), (241, 241, 241)), ((255, 255, 255), (15, 15, 15))]):
            y0 = i * 460
            d.rectangle([0, y0, 1400, y0 + 460], fill=bgc)
            x = 30
            for (w, h) in sizes:
                t = img.resize((w, h), Image.LANCZOS)
                mask = Image.new("L", (w, h), 0)
                ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=max(6, w // 40), fill=255)
                sheet.paste(t, (x, y0 + 30), mask)
                d.text((x, y0 + 40 + h), f"{w}x{h}", fill=fg, font=f)
                x += w + 40
        out = Path(f"{stem}_preview.jpg"); sheet.save(out, quality=88)
        print(f"wrote {out}  (check: readable at 168x94? one focal point? text <= 5 words?)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compose")
    c.add_argument("--bg"); c.add_argument("--bg-color", default="#111111")
    c.add_argument("--size", choices=list(SIZES), default="youtube")
    c.add_argument("--focus-x", type=float, default=0.5); c.add_argument("--focus-y", type=float, default=0.5)
    c.add_argument("--saturate", type=float, default=1.15); c.add_argument("--contrast", type=float, default=1.08)
    c.add_argument("--scrim", type=float, default=0.55, help="0 disables the dark gradient behind text")
    c.add_argument("--subject"); c.add_argument("--subject-side", choices=["left", "right", "center"], default="right")
    c.add_argument("--subject-scale", type=float, default=0.95)
    c.add_argument("--subject-outline", type=int, default=8); c.add_argument("--outline-color", default="#FFFFFF")
    c.add_argument("--text"); c.add_argument("--font", default="Anton"); c.add_argument("--weight", default=None,
                   help="variable-font instance, e.g. Black for Montserrat/Inter")
    c.add_argument("--upper", action=argparse.BooleanOptionalAction, default=True, help="--no-upper keeps case")
    c.add_argument("--color", default="#FFFFFF"); c.add_argument("--accent", default="#FFD400")
    c.add_argument("--stroke", type=float, default=0.06, help="stroke width as fraction of font size")
    c.add_argument("--stroke-color", default="#000000")
    c.add_argument("--align", choices=["left", "right", "center"], default="left")
    c.add_argument("--text-w", type=float, default=0.55, help="landscape: fraction of width for text")
    c.add_argument("--text-y", type=float, default=0.30, help="vertical: text block center (fraction)")
    c.add_argument("--text-h", type=float, default=0.22, help="vertical: max text block height (fraction)")
    c.add_argument("--line-gap", type=float, default=-0.08)
    c.add_argument("--logo"); c.add_argument("--out", required=True)
    p = sub.add_parser("preview"); p.add_argument("images", nargs="+")
    a = ap.parse_args()
    compose(a) if a.cmd == "compose" else preview(a)


if __name__ == "__main__":
    main()
