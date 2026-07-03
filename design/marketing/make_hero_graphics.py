#!/usr/bin/env python3
"""Composite marketing hero graphics for the Maharahjong pre-order landing page.

Builds three images from existing tile / mat assets:
  1. hero-banner.png            2400x1000  - fanned tile arrangement, navy/gold, left 40% clear
  2. tile-showcase-strip.png    2400x450   - clean row of tiles, alternating tilt
  3. og-image.png               1200x630   - social share card with wordmark

All compositing is done at 2x supersampling then downscaled (LANCZOS) for
antialiasing. Tiles are masked with rounded corners and given soft blurred
drop shadows. No external deps beyond Pillow.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
TILES_DIR = ROOT / "design" / "tiles" / "print-ready"
OUT_DIR = ROOT / "design" / "marketing" / "hero"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
FONT_REG = FONT_DIR / "DejaVuSans.ttf"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY_DARK = (10, 22, 42)      # deepest corner
NAVY_MID = (20, 50, 90)       # ~ #14325A, the tile-back navy
NAVY_LIGHT = (33, 74, 128)    # lighter accent navy
GOLD = (212, 168, 83)         # warm gold
GOLD_BRIGHT = (238, 199, 120)
IVORY = (245, 238, 222)

SUPERSAMPLE = 2

# ---------------------------------------------------------------------------
# Tile catalogue - relative paths under TILES_DIR
# ---------------------------------------------------------------------------

TILE = {
    "lotus1": "suit-lotus/lotus-1.png",
    "lotus4": "suit-lotus/lotus-4.png",
    "lotus7": "suit-lotus/lotus-7.png",
    "peacock1": "suit-peacock/peacock-1.png",
    "peacock3": "suit-peacock/peacock-3.png",
    "peacock6": "suit-peacock/peacock-6.png",
    "vedic2": "suit-vedic/vedic-2.png",
    "vedic5": "suit-vedic/vedic-5.png",
    "vedic8": "suit-vedic/vedic-8.png",
    "garuda": "honors/deity-garuda.png",
    "lotus_deity": "honors/deity-lotus.png",
    "nandi": "honors/deity-nandi.png",
    "wind_east": "honors/wind-east.png",
    "diwali": "bonus-festival/festival-diwali.png",
    "holi": "bonus-festival/festival-holi.png",
    "chakra_anahata": "bonus-chakra/chakra-anahata.png",
    "chakra_ajna": "bonus-chakra/chakra-ajna.png",
    "back": "tile-back/tile-back.png",
}


def tile_path(key: str) -> Path:
    return TILES_DIR / TILE[key]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_tile(key: str) -> Image.Image:
    im = Image.open(tile_path(key)).convert("RGB")
    return im


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    """Return an 'L' mode antialiased rounded-rect mask, built at 4x and
    downscaled for smooth edges."""
    ss = 4
    w, h = size
    big = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=255)
    return big.resize((w, h), Image.LANCZOS)


def rounded_tile(im: Image.Image, radius_frac: float = 0.06) -> Image.Image:
    """Apply rounded-corner alpha mask to a tile image. radius_frac is a
    fraction of the tile width."""
    w, h = im.size
    radius = int(w * radius_frac)
    mask = rounded_mask((w, h), radius)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def make_shadow_layer(
    canvas_size: tuple[int, int],
    tile_rgba: Image.Image,
    offset: tuple[int, int],
    blur: float,
    opacity: float = 0.55,
) -> Image.Image:
    """Render a blurred drop-shadow of tile_rgba's alpha channel, positioned
    at offset, on a transparent canvas the size of canvas_size."""
    shadow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    alpha = tile_rgba.split()[-1]
    black = Image.new("RGBA", tile_rgba.size, (0, 0, 0, int(255 * opacity)))
    black.putalpha(alpha.point(lambda a: int(a * opacity)))
    shadow.paste(black, offset, black)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return shadow


def paste_rgba(base: Image.Image, layer: Image.Image, pos: tuple[int, int]) -> None:
    base.alpha_composite(layer, dest=pos)


def rotate_tile(tile_rgba: Image.Image, angle_deg: float) -> Image.Image:
    return tile_rgba.rotate(
        angle_deg, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0)
    )


def radial_vertical_gradient(
    size: tuple[int, int],
    top_color,
    bottom_color,
    corner_color=None,
    corner_strength: float = 0.35,
) -> Image.Image:
    """Vertical gradient background with an optional darker vignette pulled
    toward the corners for richness."""
    w, h = size
    base = Image.new("RGB", (w, h), top_color)
    top = list(top_color)
    bottom = list(bottom_color)
    for y in range(h):
        t = y / max(h - 1, 1)
        row_color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        ImageDraw.Draw(base).line([(0, y), (w, y)], fill=row_color)

    if corner_color is not None:
        # radial vignette from center, darker at edges/corners
        vignette = Image.new("L", (w, h), 0)
        vd = ImageDraw.Draw(vignette)
        cx, cy = w / 2, h / 2
        max_r = math.hypot(cx, cy)
        # draw concentric ellipses for a soft radial falloff
        steps = 60
        for i in range(steps, 0, -1):
            t = i / steps
            r = max_r * t
            alpha = int(255 * corner_strength * t)
            vd.ellipse(
                [cx - r, cy - r * (h / w) if w else r, cx + r, cy + r * (h / w) if w else r],
                fill=alpha,
            )
        vignette = vignette.filter(ImageFilter.GaussianBlur(min(w, h) * 0.08))
        corner_layer = Image.new("RGB", (w, h), corner_color)
        base = Image.composite(corner_layer, base, vignette)
    return base


def add_gold_accents(base: Image.Image, rng: random.Random, n: int = 40) -> Image.Image:
    """Scatter faint gold dots / rangoli-like flecks for texture."""
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        r = rng.uniform(1.2, 3.8) * SUPERSAMPLE
        alpha = int(rng.uniform(35, 110))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*GOLD_BRIGHT, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.5 * SUPERSAMPLE))
    out = base.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def gold_arc_lines(base: Image.Image, rng: random.Random, region: str = "left") -> Image.Image:
    """Add a couple of thin gold arcing lines for art-deco flourish. When
    region == 'left' the arcs are concentrated in the left portion of the
    canvas so that side reads as a designed space rather than empty."""
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(5):
        if region == "left":
            cx = w * rng.uniform(-0.05, 0.30)
            cy = h * rng.uniform(0.0, 1.0)
        else:
            cx = w * rng.uniform(0.05, 0.35)
            cy = h * rng.uniform(0.6, 1.3)
        r = w * rng.uniform(0.22, 0.55)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        start = rng.uniform(0, 360)
        end = start + rng.uniform(50, 110)
        width = max(1, int(rng.uniform(1.2, 2.2) * SUPERSAMPLE))
        alpha = rng.randint(45, 85)
        d.arc(bbox, start, end, fill=(*GOLD, alpha), width=width)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.8 * SUPERSAMPLE))
    out = base.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def letter_spaced_text(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    tracking: int,
    anchor_center_x: int | None = None,
) -> tuple[int, int]:
    """Draw text with extra letter-spacing (tracking, in px). If
    anchor_center_x is given, pos[0] is ignored and the text block is
    horizontally centered on that x. Returns (width, height) drawn."""
    widths = []
    for ch in text:
        bbox = font.getbbox(ch)
        widths.append(bbox[2] - bbox[0])
    total_w = sum(widths) + tracking * (len(text) - 1)
    x, y = pos
    if anchor_center_x is not None:
        x = anchor_center_x - total_w // 2
    cursor = x
    for ch, cw in zip(text, widths):
        draw.text((cursor, y), ch, font=font, fill=fill)
        cursor += cw + tracking
    bbox_h = font.getbbox(text)
    return total_w, bbox_h[3] - bbox_h[1]


# ---------------------------------------------------------------------------
# 1. hero-banner.png  (2400 x 1000)
# ---------------------------------------------------------------------------


def build_hero_banner() -> Image.Image:
    rng = random.Random(42)
    W, H = 2400, 1000
    ss = SUPERSAMPLE
    BW, BH = W * ss, H * ss

    bg = radial_vertical_gradient(
        (BW, BH),
        top_color=NAVY_DARK,
        bottom_color=NAVY_MID,
        corner_color=(6, 14, 28),
        corner_strength=0.4,
    )
    # warm gold glow emanating from the right side (where the tiles fan out)
    glow = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx, gy = BW * 0.78, BH * 0.55
    for i in range(80, 0, -1):
        t = i / 80
        r = BW * 0.42 * t
        alpha = int(38 * (1 - t) ** 1.5)
        gd.ellipse([gx - r, gy - r * 0.8, gx + r, gy + r * 0.8], fill=(*GOLD, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(BW * 0.03))
    bg = bg.convert("RGBA")
    bg.alpha_composite(glow)
    bg = bg.convert("RGB")

    bg = add_gold_accents(bg, rng, n=90)
    bg = gold_arc_lines(bg, rng)

    canvas = bg.convert("RGBA")

    # Tile fan: place tile centers to the right ~55% of the canvas, arced,
    # with wide spacing so every tile reads clearly (no near-total occlusion).
    fan_keys = [
        "back", "vedic5", "lotus1", "garuda", "peacock3",
        "diwali", "chakra_anahata", "peacock6",
    ]

    tile_w = int(BW * 0.135)
    tile_h = int(tile_w * 32 / 23)

    n = len(fan_keys)
    # Arc parameters: fan pivot below-center-right, tiles arranged along a
    # wide arc so overlap between neighbors is modest (~35-40% of width).
    pivot_x = BW * 0.66
    pivot_y = BH * 1.85
    arc_radius = BH * 1.35
    angle_spread = 64  # degrees total - wider spread = less overlap
    start_angle = -90 - angle_spread / 2

    shadow_canvas = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    tiles_canvas = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))

    placements = []
    for i, key in enumerate(fan_keys):
        t = i / (n - 1)
        angle = start_angle + angle_spread * t
        rad = math.radians(angle)
        cx = pivot_x + arc_radius * math.cos(rad)
        cy = pivot_y + arc_radius * math.sin(rad)
        # slight per-tile jitter for a "scattered by hand" feel
        cx += rng.uniform(-10, 10) * ss
        cy += rng.uniform(-8, 8) * ss
        tilt = angle + 90 + rng.uniform(-3, 3)
        # scale the middle tiles up slightly for visual hierarchy
        scale = 1.0 + 0.10 * math.sin(t * math.pi)
        placements.append((key, cx, cy, tilt, scale))

    for key, cx, cy, tilt, scale in placements:
        base_im = load_tile(key)
        w = int(tile_w * scale)
        h = int(w * 32 / 23)
        base_im = base_im.resize((w, h), Image.LANCZOS)
        rt = rounded_tile(base_im, radius_frac=0.065)
        rot = rotate_tile(rt, tilt)

        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))

        shadow = make_shadow_layer(
            (BW, BH),
            rot,
            offset=(pos[0] + int(10 * ss), pos[1] + int(16 * ss)),
            blur=14 * ss / 2,
            opacity=0.5,
        )
        shadow_canvas.alpha_composite(shadow)

    # composite shadows first, then tiles on top (so no tile shadow falls on
    # top of a later tile incorrectly ordered -- draw tiles back-to-front
    # matching fan order so overlap looks natural)
    canvas.alpha_composite(shadow_canvas)
    for key, cx, cy, tilt, scale in placements:
        base_im = load_tile(key)
        w = int(tile_w * scale)
        h = int(w * 32 / 23)
        base_im = base_im.resize((w, h), Image.LANCZOS)
        rt = rounded_tile(base_im, radius_frac=0.065)
        rot = rotate_tile(rt, tilt)
        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))
        # subtle thin gold edge highlight: draw a slightly larger soft gold
        # rounded rect behind tile edges is skipped for cleanliness; rely on
        # shadow + tile art itself.
        canvas.alpha_composite(rot, dest=pos)

    # Gentle vignette darkening toward the far left edge only (last 15%),
    # to keep a premium framed look without flattening the left 40% that
    # needs to stay legible/clear for the HTML headline overlay.
    fade_w = int(BW * 0.18)
    overlay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(fade_w):
        t = 1 - (x / fade_w)
        a = int(50 * t)
        od.line([(x, 0), (x, BH)], fill=(*NAVY_DARK, a))
    canvas.alpha_composite(overlay)

    final = canvas.convert("RGB").resize((W, H), Image.LANCZOS)
    return final


# ---------------------------------------------------------------------------
# 2. tile-showcase-strip.png  (2400 x 450)
# ---------------------------------------------------------------------------


def build_showcase_strip() -> Image.Image:
    rng = random.Random(7)
    W, H = 2400, 450
    ss = SUPERSAMPLE
    BW, BH = W * ss, H * ss

    canvas = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))

    keys = [
        "back", "lotus4", "peacock1", "vedic2", "garuda",
        "diwali", "chakra_ajna", "peacock6", "lotus_deity", "vedic8",
    ]
    n = len(keys)

    tile_h = int(BH * 0.72)
    tile_w = int(tile_h * 23 / 32)

    margin_x = int(BW * 0.03)
    usable_w = BW - 2 * margin_x
    slot_w = usable_w / n

    shadow_canvas = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    placements = []
    for i, key in enumerate(keys):
        cx = margin_x + slot_w * (i + 0.5)
        cy = BH / 2 + rng.uniform(-6, 6) * ss
        tilt = 3.0 if i % 2 == 0 else -3.0
        tilt += rng.uniform(-1.0, 1.0)
        placements.append((key, cx, cy, tilt))

    for key, cx, cy, tilt in placements:
        im = load_tile(key).resize((tile_w, tile_h), Image.LANCZOS)
        rt = rounded_tile(im, radius_frac=0.06)
        rot = rotate_tile(rt, tilt)
        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))
        shadow = make_shadow_layer(
            (BW, BH), rot,
            offset=(pos[0] + int(6 * ss), pos[1] + int(10 * ss)),
            blur=9 * ss / 2, opacity=0.4,
        )
        shadow_canvas.alpha_composite(shadow)

    canvas.alpha_composite(shadow_canvas)
    for key, cx, cy, tilt in placements:
        im = load_tile(key).resize((tile_w, tile_h), Image.LANCZOS)
        rt = rounded_tile(im, radius_frac=0.06)
        rot = rotate_tile(rt, tilt)
        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))
        canvas.alpha_composite(rot, dest=pos)

    final = canvas.resize((W, H), Image.LANCZOS)
    return final  # RGBA, transparent background


# ---------------------------------------------------------------------------
# 3. og-image.png  (1200 x 630)
# ---------------------------------------------------------------------------


def build_og_image() -> Image.Image:
    rng = random.Random(99)
    W, H = 1200, 630
    ss = SUPERSAMPLE
    BW, BH = W * ss, H * ss

    bg = radial_vertical_gradient(
        (BW, BH),
        top_color=NAVY_DARK,
        bottom_color=NAVY_MID,
        corner_color=(6, 14, 28),
        corner_strength=0.45,
    )
    bg = add_gold_accents(bg, rng, n=60)
    bg = gold_arc_lines(bg, rng, region="left")
    canvas = bg.convert("RGBA")

    keys = ["back", "garuda", "lotus1", "diwali", "peacock3"]
    n = len(keys)
    tile_h = int(BH * 0.46)
    tile_w = int(tile_h * 23 / 32)

    # Arrange tiles fanned along the bottom-right area only, well clear of
    # the left ~55% reserved for the wordmark and subtitle.
    pivot_x = BW * 0.86
    pivot_y = BH * 1.75
    arc_radius = BH * 1.25
    angle_spread = 40
    start_angle = -90 - angle_spread / 2

    shadow_canvas = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    placements = []
    for i, key in enumerate(keys):
        t = i / (n - 1)
        angle = start_angle + angle_spread * t
        rad = math.radians(angle)
        cx = pivot_x + arc_radius * math.cos(rad)
        cy = pivot_y + arc_radius * math.sin(rad)
        cx += rng.uniform(-6, 6) * ss
        tilt = angle + 90 + rng.uniform(-2, 2)
        placements.append((key, cx, cy, tilt))

    for key, cx, cy, tilt in placements:
        im = load_tile(key).resize((tile_w, tile_h), Image.LANCZOS)
        rt = rounded_tile(im, radius_frac=0.07)
        rot = rotate_tile(rt, tilt)
        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))
        shadow = make_shadow_layer(
            (BW, BH), rot,
            offset=(pos[0] + int(8 * ss), pos[1] + int(12 * ss)),
            blur=10 * ss / 2, opacity=0.5,
        )
        shadow_canvas.alpha_composite(shadow)

    canvas.alpha_composite(shadow_canvas)
    for key, cx, cy, tilt in placements:
        im = load_tile(key).resize((tile_w, tile_h), Image.LANCZOS)
        rt = rounded_tile(im, radius_frac=0.07)
        rot = rotate_tile(rt, tilt)
        pos = (int(cx - rot.width / 2), int(cy - rot.height / 2))
        canvas.alpha_composite(rot, dest=pos)

    # darken left/top area a bit for text legibility
    overlay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    fade_w = int(BW * 0.58)
    for x in range(fade_w):
        t = 1 - (x / fade_w)
        a = int(95 * t)
        od.line([(x, 0), (x, BH)], fill=(*NAVY_DARK, a))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)

    title_font = ImageFont.truetype(str(FONT_BOLD), int(80 * ss))
    subtitle_font = ImageFont.truetype(str(FONT_REG), int(32 * ss))

    text_x = int(BW * 0.07)
    title_y = int(BH * 0.42)

    # subtle soft shadow behind the wordmark for depth
    shadow_text = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    std = ImageDraw.Draw(shadow_text)
    letter_spaced_text(
        std, (text_x + int(4 * ss), title_y + int(4 * ss)), "MAHARAHJONG",
        title_font, (0, 0, 0, 140), tracking=int(10 * ss),
    )
    shadow_text = shadow_text.filter(ImageFilter.GaussianBlur(3 * ss))
    canvas.alpha_composite(shadow_text)

    draw = ImageDraw.Draw(canvas)
    tw, th = letter_spaced_text(
        draw, (text_x, title_y), "MAHARAHJONG",
        title_font, (*GOLD_BRIGHT, 255), tracking=int(10 * ss),
    )

    subtitle_y = title_y + int(th * 1.9)
    letter_spaced_text(
        draw, (text_x, subtitle_y), "PRE-ORDER SOON  ·  MAHARAHJONG.COM",
        subtitle_font, (*IVORY, 235), tracking=int(4 * ss),
    )

    # thin gold rule under the wordmark
    rule_y = title_y - int(18 * ss)
    draw.line(
        [(text_x, rule_y), (text_x + int(tw * 0.34), rule_y)],
        fill=(*GOLD, 220), width=int(3 * ss),
    )

    final = canvas.convert("RGB").resize((W, H), Image.LANCZOS)
    return final


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Building hero-banner.png ...")
    hero = build_hero_banner()
    hero.save(OUT_DIR / "hero-banner.png")
    print(f"  saved {hero.size}")

    print("Building tile-showcase-strip.png ...")
    strip = build_showcase_strip()
    strip.save(OUT_DIR / "tile-showcase-strip.png")
    print(f"  saved {strip.size}")

    print("Building og-image.png ...")
    og = build_og_image()
    og.save(OUT_DIR / "og-image.png")
    print(f"  saved {og.size}")

    print("Done.")


if __name__ == "__main__":
    main()
