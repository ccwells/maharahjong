#!/usr/bin/env python3
"""Generate a print-proof PDF of all 51 Maharahjong tile designs.

Each tile is reproduced at its exact physical printed size (32 × 23 mm) on
A4 landscape pages (297 × 210 mm) at 300 DPI.  All 51 tiles fit on a single
page in an 8 × 7 grid.  Tiles are grouped and ordered by category; a
thin rule separates each group.

Source:  design/tiles/print-ready/   (default — ivory/cream background)
Output:  design/tiles/proof-sheet.pdf

Usage:
    python3.10 design/tiles/make_proof_sheet.py
    python3.10 design/tiles/make_proof_sheet.py --out /tmp/proof.pdf
    python3.10 design/tiles/make_proof_sheet.py --dpi 150   # faster preview
    python3.10 design/tiles/make_proof_sheet.py --src design/tiles/transparent
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TILES_DIR = Path(__file__).parent
DEFAULT_SRC = TILES_DIR / "print-ready"
DEFAULT_OUT = TILES_DIR / "proof-sheet.pdf"

# ---------------------------------------------------------------------------
# Physical dimensions (mm)
# ---------------------------------------------------------------------------
PAGE_W_MM, PAGE_H_MM = 297.0, 210.0   # A4 landscape
TILE_W_MM, TILE_H_MM = 32.0, 23.0    # physical tile face
MARGIN_MM = 5.0
COL_GAP_MM = 1.5
ROW_GAP_MM = 1.0
LABEL_H_MM = 3.0   # below each tile — small text

# ---------------------------------------------------------------------------
# Tile order: (category_dir, stem_prefix, display_label, sort_key_fn)
# ---------------------------------------------------------------------------
TILE_ORDER: list[tuple[str, str]] = [
    # category dir     display name template
    ("suit-lotus",     "Lotus"),
    ("suit-peacock",   "Peacock"),
    ("suit-vedic",     "Vedic"),
    ("honors",         ""),       # mixed winds + deities — handled below
    ("bonus-festival", "Festival"),
    ("bonus-chakra",   "Chakra"),
    ("tile-back",      "Tile Back"),
]

# Explicit order within honors (winds first, then deities)
HONORS_ORDER = [
    "wind-east", "wind-south", "wind-west", "wind-north",
    "deity-garuda", "deity-nandi", "deity-lotus",
]

# Explicit order within bonus-festival (calendar-ish order)
FESTIVAL_ORDER = [
    "festival-makar-sankranti",
    "festival-holi",
    "festival-onam",
    "festival-ganesh-chaturthi",
    "festival-navratri",
    "festival-diwali",
    "festival-raksha-bandhan",
    "festival-pongal",
]

# Explicit order for chakras (root → crown → universal)
CHAKRA_ORDER = [
    "chakra-muladhara",
    "chakra-svadhisthana",
    "chakra-manipura",
    "chakra-anahata",
    "chakra-vishuddha",
    "chakra-ajna",
    "chakra-sahasrara",
    "chakra-universal",
]


def _pretty_label(category: str, stem: str) -> str:
    """Return a short human-readable tile label, e.g. 'Lotus 3', 'Wind East'."""
    parts = stem.split("-")
    if category == "suit-lotus":
        return f"Lotus {parts[-1]}"
    if category == "suit-peacock":
        return f"Peacock {parts[-1]}"
    if category == "suit-vedic":
        return f"Vedic {parts[-1]}"
    if category == "honors":
        kind = parts[0].capitalize()   # "wind" or "deity"
        name = " ".join(p.capitalize() for p in parts[1:])
        return f"{kind} {name}"
    if category == "bonus-festival":
        name = " ".join(p.capitalize() for p in parts[1:])
        return f"{name}"
    if category == "bonus-chakra":
        name = " ".join(p.capitalize() for p in parts[1:])
        return f"{name}"
    if category == "tile-back":
        return "Tile Back"
    return stem


def collect_ordered_tiles(src: Path) -> list[tuple[Path, str]]:
    """Return [(path, label), ...] for all tiles in display order."""
    result: list[tuple[Path, str]] = []
    for cat, _ in TILE_ORDER:
        cat_dir = src / cat
        if not cat_dir.is_dir():
            continue

        if cat == "honors":
            stems = HONORS_ORDER
        elif cat == "bonus-festival":
            stems = FESTIVAL_ORDER
        elif cat == "bonus-chakra":
            stems = CHAKRA_ORDER
        elif cat == "tile-back":
            stems = ["tile-back"]
        else:
            # Numbered suits: sort by trailing integer
            stems = sorted(
                (p.stem for p in cat_dir.glob("*.png")),
                key=lambda s: int(s.split("-")[-1]) if s.split("-")[-1].isdigit() else 0,
            )

        for stem in stems:
            p = cat_dir / f"{stem}.png"
            if p.exists():
                result.append((p, _pretty_label(cat, stem)))

    return result


def _category_of(tile_path: Path, src: Path) -> str:
    return tile_path.relative_to(src).parts[0]


def build_page(
    tiles: list[tuple[Path, str, bool]],  # (path, label, is_first_in_category)
    *,
    dpi: int,
    font_sm,
    font_title,
    page_num: int,
    total_pages: int,
) -> "Image":  # type: ignore[name-defined]
    """Compose one proof-sheet page and return it as a PIL Image."""
    from PIL import Image, ImageDraw

    px = dpi / 25.4  # pixels per mm

    pw = round(PAGE_W_MM * px)
    ph = round(PAGE_H_MM * px)

    tile_w = round(TILE_W_MM * px)
    tile_h = round(TILE_H_MM * px)
    margin = round(MARGIN_MM * px)
    col_gap = round(COL_GAP_MM * px)
    row_gap = round(ROW_GAP_MM * px)
    label_h = round(LABEL_H_MM * px)

    col_step = tile_w + col_gap
    row_step = tile_h + row_gap + label_h

    # How many columns fit?
    n_cols = (pw - 2 * margin + col_gap) // col_step

    page = Image.new("RGB", (pw, ph), "white")
    draw = ImageDraw.Draw(page)

    # ── Title ──────────────────────────────────────────────────────────────
    title_text = "Maharahjong — Tile Proof Sheet"
    if total_pages > 1:
        title_text += f"  (page {page_num}/{total_pages})"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_h = title_bbox[3] - title_bbox[1]
    draw.text(
        (margin, margin),
        title_text,
        fill=(30, 30, 30),
        font=font_title,
    )

    # Subtitle: "32 × 23 mm · actual print size · 300 DPI"
    sub_text = f"32 × 23 mm · actual print size · {dpi} DPI · {len(tiles)} tiles"
    draw.text(
        (margin, margin + title_h + round(1.5 * px)),
        sub_text,
        fill=(120, 120, 120),
        font=font_sm,
    )

    header_h = margin + round(7 * px)   # 7 mm for title + subtitle

    # ── Tile grid ──────────────────────────────────────────────────────────
    # Category rule colours (subtle, matches brand palette)
    CAT_COLOURS: dict[str, tuple[int, int, int]] = {
        "suit-lotus":     (200,  80, 150),   # magenta-pink
        "suit-peacock":   ( 30, 140, 140),   # teal
        "suit-vedic":     (100,  50, 160),   # purple
        "honors":         (180, 120,  30),   # saffron gold
        "bonus-festival": (210,  80,  50),   # festive orange-red
        "bonus-chakra":   ( 60, 100, 180),   # indigo
        "tile-back":      ( 20,  50,  90),   # deep navy
    }

    col_idx = row_idx = 0
    last_cat = None

    for tile_path, label, is_first_cat in tiles:
        cat = tile_path.parent.name
        x0 = margin + col_idx * col_step
        y0 = header_h + row_idx * row_step

        # ── Category separator rule ────────────────────────────────────────
        if is_first_cat and cat != last_cat and col_idx == 0 and row_idx > 0:
            rule_y = y0 - round(row_gap * 0.45)
            rule_colour = CAT_COLOURS.get(cat, (150, 150, 150))
            draw.line(
                [(margin, rule_y), (pw - margin, rule_y)],
                fill=rule_colour,
                width=max(1, round(0.3 * px)),
            )
        last_cat = cat

        # ── Tile image ─────────────────────────────────────────────────────
        with Image.open(tile_path) as tile_img:
            # Paste onto a white background first (handles transparent tiles)
            bg = Image.new("RGB", (tile_w, tile_h), (255, 255, 255))
            thumb = tile_img.convert("RGBA").resize(
                (tile_w, tile_h), Image.LANCZOS
            )
            bg.paste(thumb, mask=thumb.split()[3])
            page.paste(bg, (x0, y0))

        # ── Thin border around tile ────────────────────────────────────────
        draw.rectangle(
            [x0, y0, x0 + tile_w - 1, y0 + tile_h - 1],
            outline=(180, 180, 180),
            width=1,
        )

        # ── Label ──────────────────────────────────────────────────────────
        label_colour = CAT_COLOURS.get(cat, (80, 80, 80))
        label_bbox = draw.textbbox((0, 0), label, font=font_sm)
        label_w = label_bbox[2] - label_bbox[0]
        lx = x0 + (tile_w - label_w) // 2
        ly = y0 + tile_h + round(1 * px)
        draw.text((lx, ly), label, fill=label_colour, font=font_sm)

        # ── Advance grid position ──────────────────────────────────────────
        col_idx += 1
        if col_idx >= n_cols:
            col_idx = 0
            row_idx += 1

    return page


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a print-proof PDF of all Maharahjong tile designs"
    )
    ap.add_argument(
        "--src",
        type=Path,
        default=DEFAULT_SRC,
        metavar="DIR",
        help=f"source tile directory (default: {DEFAULT_SRC.name}/)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        metavar="FILE",
        help=f"output PDF path (default: {DEFAULT_OUT.name})",
    )
    ap.add_argument(
        "--dpi",
        type=int,
        default=300,
        metavar="N",
        help="render DPI (default: 300; use 150 for a quick preview)",
    )
    args = ap.parse_args()

    # ── Dependency check ────────────────────────────────────────────────────
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: F401
    except ImportError:
        print("ERROR: Pillow is required.  pip install Pillow", file=sys.stderr)
        return 1

    from PIL import ImageFont

    # ── Font loading ────────────────────────────────────────────────────────
    def _load_font(size_pt: float) -> "ImageFont.FreeTypeFont":
        size_px = round(size_pt * args.dpi / 72)
        for path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]:
            try:
                return ImageFont.truetype(path, size_px)
            except OSError:
                continue
        return ImageFont.load_default()

    font_title = _load_font(10)   # ~10pt title
    font_sm    = _load_font(6)    # ~6pt tile labels

    # ── Collect and order tiles ─────────────────────────────────────────────
    ordered = collect_ordered_tiles(args.src)
    if not ordered:
        print(f"ERROR: No tiles found in {args.src}", file=sys.stderr)
        return 1
    print(f"Found {len(ordered)} tiles in {args.src.name}/")

    # Mark the first tile of each new category for rule drawing.
    tagged: list[tuple[Path, str, bool]] = []
    prev_cat = None
    for path, label in ordered:
        cat = path.parent.name
        tagged.append((path, label, cat != prev_cat))
        prev_cat = cat

    # ── Paginate ────────────────────────────────────────────────────────────
    px = args.dpi / 25.4
    col_step = round(TILE_W_MM * px) + round(COL_GAP_MM * px)
    row_step = round(TILE_H_MM * px) + round(ROW_GAP_MM * px) + round(LABEL_H_MM * px)
    margin = round(MARGIN_MM * px)
    pw = round(PAGE_W_MM * px)
    header_h = round(7 * px)   # 7 mm for header area
    n_cols = (pw - 2 * margin + round(COL_GAP_MM * px)) // col_step
    n_rows = (round(PAGE_H_MM * px) - round(MARGIN_MM * px) - header_h - round(MARGIN_MM * px) + round(ROW_GAP_MM * px)) // row_step
    tiles_per_page = n_cols * n_rows

    pages_data: list[list[tuple[Path, str, bool]]] = []
    for i in range(0, len(tagged), tiles_per_page):
        pages_data.append(tagged[i : i + tiles_per_page])

    total_pages = len(pages_data)
    print(
        f"Layout: {n_cols} cols × {n_rows} rows = {tiles_per_page} tiles/page → "
        f"{total_pages} page(s)"
    )
    print(f"Rendering at {args.dpi} DPI ({round(PAGE_W_MM * px)} × {round(PAGE_H_MM * px)} px/page)...")

    # ── Render pages ────────────────────────────────────────────────────────
    rendered: list = []
    for i, page_tiles in enumerate(pages_data, 1):
        print(f"  Page {i}/{total_pages} ({len(page_tiles)} tiles)...", end=" ", flush=True)
        page_img = build_page(
            page_tiles,
            dpi=args.dpi,
            font_sm=font_sm,
            font_title=font_title,
            page_num=i,
            total_pages=total_pages,
        )
        rendered.append(page_img)
        print("OK")

    # ── Save PDF ─────────────────────────────────────────────────────────────
    args.out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving → {args.out} ...", end=" ", flush=True)
    rendered[0].save(
        args.out,
        format="PDF",
        save_all=True,
        append_images=rendered[1:],
        resolution=args.dpi,
    )
    size_mb = args.out.stat().st_size / (1024 * 1024)
    print(f"OK ({size_mb:.1f} MB)")
    print(f"\nDone! Open: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
