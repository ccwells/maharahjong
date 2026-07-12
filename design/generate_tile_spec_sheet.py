#!/usr/bin/env python3
"""
Generate manufacturer spec sheet assets for the Maharajong blank tile.

Outputs (in design/manufacturer-docs/):
  tile-blank-technical-drawing.svg   — precise SVG engineering drawing for manufacturing
  tile-blank-spec-sheet-rendered.png — Grok-rendered product image for human review

Usage:
    python3 design/generate_tile_spec_sheet.py           # generate both
    python3 design/generate_tile_spec_sheet.py --svg-only
    python3 design/generate_tile_spec_sheet.py --img-only
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Set VARIANT to "variant-01" or "variant-02" (or pass --variant on the CLI)
DEFAULT_VARIANT = "variant-01"
OUT_DIR = Path(__file__).parent / DEFAULT_VARIANT / "manufacturer-docs"

# ---------------------------------------------------------------------------
# Tile specification constants
# ---------------------------------------------------------------------------
TILE_W_MM    = 32   # width  (face, left-right)
TILE_H_MM    = 23   # height (face, top-bottom)
TILE_D_MM    = 13   # depth  (thickness)
LAYER_1_MM   = 3    # ivory face
LAYER_2_MM   = 1    # gold hairline
LAYER_3_MM   = 6    # lapis-navy core
LAYER_4_MM   = 3    # ivory back
TOL_MM       = 0.2  # dimensional tolerance ±
WEIGHT_G_MIN = 16
WEIGHT_G_MAX = 19

# Colors
C_IVORY      = "#F5EDD8"
C_IVORY_DRK  = "#E8DFC8"   # for back face (slight shadow)
C_GOLD       = "#D4AF37"
C_GOLD_LIGHT = "#F0D060"
C_NAVY       = "#1C2E5E"
C_NAVY_MID   = "#263D7A"
C_BLACK      = "#1A1A1A"
C_GRAY       = "#555555"
C_LIGHTGRAY  = "#AAAAAA"
C_DIMLINE    = "#222222"
C_BGPAPER    = "#FAFAF8"
C_BORDER     = "#222222"
C_TITLE_BG   = "#F0EFE8"
# Variant-02: clear acrylic back — represented as navy-tinted with hatch
C_CLEAR_FILL = "#D6E6F0"   # light blue-white: navy core seen through 3mm clear PMMA
C_CLEAR_HATCH = "#8AAEC8"  # hatch lines indicating transparent material


# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def _rect(x, y, w, h, fill, stroke=None, sw=1, rx=0, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
    r = f' rx="{rx}"' if rx else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{s}{r} {extra}/>'


def _line(x1, y1, x2, y2, stroke=C_DIMLINE, sw=1.2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def _text(x, y, content, size=12, fill=C_BLACK, anchor="middle",
          weight="normal", family="'Helvetica Neue', Arial, sans-serif", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" font-family="{family}" {extra}>'
            f'{content}</text>')


def _dim_line_h(x1, x2, y, label, ext_len=20, text_size=11):
    """Horizontal dimension line between x1 and x2 at height y."""
    mid = (x1 + x2) / 2
    lines = [
        # extension lines
        _line(x1, y - ext_len, x1, y + ext_len, sw=0.8),
        _line(x2, y - ext_len, x2, y + ext_len, sw=0.8),
        # dimension line with arrows
        (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{C_DIMLINE}" '
         f'stroke-width="1.2" marker-end="url(#arr)" marker-start="url(#arr-rev)"/>'),
        _text(mid, y - 6, label, size=text_size),
    ]
    return "\n".join(lines)


def _dim_line_v(y1, y2, x, label, ext_len=20, text_size=11):
    """Vertical dimension line between y1 and y2 at position x."""
    mid = (y1 + y2) / 2
    lines = [
        _line(x - ext_len, y1, x + ext_len, y1, sw=0.8),
        _line(x - ext_len, y2, x + ext_len, y2, sw=0.8),
        (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{C_DIMLINE}" '
         f'stroke-width="1.2" marker-end="url(#arr)" marker-start="url(#arr-rev)"/>'),
        (f'<text x="{x - 8}" y="{mid}" font-size="{text_size}" fill="{C_BLACK}" '
         f'text-anchor="middle" font-family="\'Helvetica Neue\', Arial, sans-serif" '
         f'transform="rotate(-90, {x - 8}, {mid})">{label}</text>'),
    ]
    return "\n".join(lines)


def _leader(x1, y1, x2, y2, label, size=11, anchor="start"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C_GRAY}" '
            f'stroke-width="0.9" stroke-dasharray="4,2"/>'
            f'\n' + _text(x2 + (6 if anchor == "start" else -6), y2 + 4,
                          label, size=size, anchor=anchor, fill=C_GRAY))


# ---------------------------------------------------------------------------
# SVG technical drawing
# ---------------------------------------------------------------------------

def generate_svg(variant: str = "variant-01") -> str:
    SC = 8            # px per mm — reduced for Letter landscape
    SC2 = 16          # px per mm (layer detail at 2:1)
    W  = TILE_W_MM * SC    # 320
    H  = TILE_H_MM * SC    # 230
    D  = TILE_D_MM * SC    # 130

    # Layer heights at main scale
    l1 = LAYER_1_MM * SC   # 30 – ivory face
    l2 = LAYER_2_MM * SC   # 10 – gold
    l3 = LAYER_3_MM * SC   # 60 – navy
    l4 = LAYER_4_MM * SC   # 30 – ivory back

    # Layer heights at detail scale
    d1 = LAYER_1_MM * SC2
    d2 = LAYER_2_MM * SC2
    d3 = LAYER_3_MM * SC2
    d4 = LAYER_4_MM * SC2

    # Variant-specific Layer 4 rendering
    is_v2 = (variant == "variant-02")
    l4_fill   = C_CLEAR_FILL if is_v2 else C_IVORY_DRK
    l4_label  = "L4: CRYSTAL CLEAR ACRYLIC" if is_v2 else "L4: IVORY ACRYLIC"
    l4_spec   = (f"Crystal-clear PMMA, {LAYER_4_MM} mm — water-white, zero haze"
                 if is_v2 else
                 f"Ivory/cream, {LAYER_4_MM} mm — match Layer 1")
    l4_back_note = ("Back: apparent navy (L3 visible through clear L4)"
                    if is_v2 else
                    "Back: ivory (matches face)")
    variant_label = "Variant 02: Ivory / Gold / Navy / Clear" if is_v2 else "Variant 01: Ivory / Gold / Navy / Ivory"
    dwg_number    = "MJ-TILE-BLK-002" if is_v2 else "MJ-TILE-BLK-001"
    back_label    = ("\u2190 BACK (NAVY THROUGH CLEAR) \u2192"
                     if is_v2 else "\u2190 BACK \u2192")

    # Canvas sized for Letter landscape (11\u00d78.5 in) at 100 units/inch
    CANVAS_W = 1100
    CANVAS_H = 850

    # Left panel view origins (x: 20–590, y: 95–660)
    VX = 70    # left edge of face/edge views
    VY = 115   # top of face view

    # Face view  (top view, 32×23mm)
    FX, FY = VX, VY

    # Long-edge cross-section (32×13mm): below face view
    EX = VX
    EY = FY + H + 85

    # Short-edge cross-section (23×13mm): right of long-edge
    SEX = EX + W + 60
    SEY = EY

    # Vertical panel divider x position (right of View C)
    DIVIDER_X = 614

    # Right panel: layer detail diagram
    DX = 640          # left edge of detail diagram
    DY = VY           # aligned with VY
    DETAIL_SECTION_W = 155
    DETAIL_H = TILE_D_MM * SC2   # 13×16 = 208px

    # Right panel: spec table (starts below detail diagram)
    SPEC_X     = DX - 4          # left edge of spec table
    SPEC_Y     = DY + DETAIL_H + 36  # start below detail
    SPEC_W     = CANVAS_W - SPEC_X - 22   # to near-right margin
    SPEC_ROW_H = 19               # compact row height
    SPEC_COL2  = SPEC_X + 195     # value column x

    # Footer: notes + title block
    FOOTER_Y = 700
    FOOTER_H = CANVAS_H - FOOTER_Y - 18
    TB_X = 510
    TB_Y = FOOTER_Y
    TB_W = CANVAS_W - TB_X - 20
    TB_H = FOOTER_H

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="11in" height="8.5in" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">',

        # ── Arrowhead markers ────────────────────────────────────────────────
        f'''<defs>
  <marker id="arr" markerWidth="8" markerHeight="6"
          refX="8" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#1A1A1A"/>
  </marker>
  <marker id="arr-rev" markerWidth="8" markerHeight="6"
          refX="0" refY="3" orient="auto">
    <polygon points="8 0, 0 3, 8 6" fill="#1A1A1A"/>
  </marker>
  <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">
    <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#00000030"/>
  </filter>
  <pattern id="clear-hatch" width="8" height="8" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8"
          stroke="{C_CLEAR_HATCH}" stroke-width="1.2"/>
  </pattern>
</defs>''',

        # ── Background ───────────────────────────────────────────────────────
        _rect(0, 0, CANVAS_W, CANVAS_H, C_BGPAPER),
        # Outer border
        _rect(10, 10, CANVAS_W - 20, CANVAS_H - 20, "none", C_BORDER, sw=2),
        # Inner border
        _rect(20, 20, CANVAS_W - 40, CANVAS_H - 40, "none", C_BORDER, sw=0.5),

        # ── Sheet title ──────────────────────────────────────────────────────
        _text(CANVAS_W // 2, 55,
              "MAHARAJONG — BLANK TILE SPECIFICATION",
              size=18, weight="bold", fill=C_BLACK),
        _text(CANVAS_W // 2, 72,
              variant_label,
              size=12, fill=C_NAVY, weight="bold"),
        _text(CANVAS_W // 2, 88,
              f"Drawing No: {dwg_number}  |  Scale 1:1 (main views)  |  Units: mm",
              size=11, fill=C_GRAY),

        # ── Section dividers ─────────────────────────────────────────────────
        _line(DIVIDER_X, 100, DIVIDER_X, FOOTER_Y - 4, C_LIGHTGRAY, sw=0.8, dash="6,3"),
        _line(20, FOOTER_Y - 6, CANVAS_W - 20, FOOTER_Y - 6, C_LIGHTGRAY, sw=0.8),

        # ════════════════════════════════════════════════════════════════════
        # VIEW 1: FACE VIEW (Top / Front face — 32mm × 23mm)
        # ════════════════════════════════════════════════════════════════════
        _text(FX + W // 2, FY - 14,
              "VIEW A — FACE (Top)", size=11, weight="bold", fill=C_GRAY),

        # Face fill: ivory (plain black engineering border — no artwork border on blank tile spec)
        _rect(FX, FY, W, H, C_IVORY, C_BLACK, sw=1.5),
        # Centre cross (registration marks, light)
        _line(FX + W // 2 - 12, FY + H // 2, FX + W // 2 + 12, FY + H // 2,
              C_LIGHTGRAY, sw=0.5),
        _line(FX + W // 2, FY + H // 2 - 12, FX + W // 2, FY + H // 2 + 12,
              C_LIGHTGRAY, sw=0.5),

        # UV print area label
        _text(FX + W // 2, FY + H // 2 + 5,
              "UV PRINT AREA", size=9, fill=C_LIGHTGRAY, weight="bold"),
        _text(FX + W // 2, FY + H // 2 + 18,
              "DO NOT MARK", size=8, fill=C_LIGHTGRAY),

        # "FACE" label corner
        _text(FX + 10, FY + 14, "FACE", size=8, fill=C_GOLD, anchor="start",
              weight="bold"),

        # ── Dimension lines for face view ────────────────────────────────────
        # Width: 32mm (below face view)
        _dim_line_h(FX, FX + W, FY + H + 28, f"32.0 ±{TOL_MM}"),
        # Height: 23mm (left of face view)
        _dim_line_v(FY, FY + H, FX - 34, f"23.0 ±{TOL_MM}"),

        # ════════════════════════════════════════════════════════════════════
        # VIEW 2: LONG EDGE CROSS-SECTION (32mm × 13mm, showing all 4 layers)
        # ════════════════════════════════════════════════════════════════════
        _text(EX + W // 2, EY - 14,
              "VIEW B — LONG EDGE CROSS-SECTION (32mm × 13mm)",
              size=11, weight="bold", fill=C_GRAY),

        # Layer 1: Ivory face (top, l1 px)
        _rect(EX, EY, W, l1, C_IVORY, C_BLACK, sw=0.6),
        # Layer 2: Gold hairline
        _rect(EX, EY + l1, W, l2, C_GOLD, C_BLACK, sw=0.6),
        # Layer 3: Navy core
        _rect(EX, EY + l1 + l2, W, l3, C_NAVY, C_BLACK, sw=0.6),
        # Layer 4: back (ivory V01 / clear V02)
        _rect(EX, EY + l1 + l2 + l3, W, l4, l4_fill, C_BLACK, sw=0.6),
        # Clear hatch overlay for V02
        *([
            _rect(EX, EY + l1 + l2 + l3, W, l4,
                  "url(#clear-hatch)", "none"),
        ] if is_v2 else []),

        # Overall border
        _rect(EX, EY, W, D, "none", C_BLACK, sw=1.5),

        # Face / back labels inside
        _text(EX + W // 2, EY + l1 - 6,
              "← FACE (UV PRINT SURFACE) →", size=8, fill=C_IVORY_DRK),
        _text(EX + W // 2, EY + l1 + l2 + l3 // 2 + 4,
              "CORE", size=9, fill="#AABDE0"),
        _text(EX + W // 2, EY + D - 8,
              back_label, size=8, fill=C_GRAY),

        # Width dimension (same as face, aligned below)
        _dim_line_h(EX, EX + W, EY + D + 28, f"32.0 ±{TOL_MM}"),
        # Depth/thickness dimension (left of this view)
        _dim_line_v(EY, EY + D, EX - 34, f"13.0 ±{TOL_MM}"),

        # ════════════════════════════════════════════════════════════════════
        # VIEW 3: SHORT EDGE CROSS-SECTION (23mm × 13mm)
        # ════════════════════════════════════════════════════════════════════
        _text(SEX + (TILE_H_MM * SC) // 2, SEY - 14,
              "VIEW C — SHORT EDGE (23mm × 13mm)",
              size=11, weight="bold", fill=C_GRAY),

        _rect(SEX, SEY, TILE_H_MM * SC, l1, C_IVORY, C_BLACK, sw=0.6),
        _rect(SEX, SEY + l1, TILE_H_MM * SC, l2, C_GOLD, C_BLACK, sw=0.6),
        _rect(SEX, SEY + l1 + l2, TILE_H_MM * SC, l3, C_NAVY, C_BLACK, sw=0.6),
        _rect(SEX, SEY + l1 + l2 + l3, TILE_H_MM * SC, l4, l4_fill, C_BLACK, sw=0.6),
        *([
            _rect(SEX, SEY + l1 + l2 + l3, TILE_H_MM * SC, l4,
                  "url(#clear-hatch)", "none"),
        ] if is_v2 else []),
        _rect(SEX, SEY, TILE_H_MM * SC, D, "none", C_BLACK, sw=1.5),

        # Short edge dimension
        _dim_line_h(SEX, SEX + TILE_H_MM * SC, SEY + D + 28, f"23.0 ±{TOL_MM}"),

        # ════════════════════════════════════════════════════════════════════
        # LAYER DETAIL (right panel, ~2:1 scale)
        # ════════════════════════════════════════════════════════════════════
        _text(DX + DETAIL_SECTION_W // 2, DY - 14,
              "DETAIL D — LAYER CROSS-SECTION (Scale 2:1)",
              size=11, weight="bold", fill=C_GRAY),

        # Draw a partial-width slice showing all 4 layers at 2× scale
        _rect(DX, DY, DETAIL_SECTION_W, d1, C_IVORY, C_BLACK, sw=0.8),
        _rect(DX, DY + d1, DETAIL_SECTION_W, d2, C_GOLD, C_BLACK, sw=0.8),
        _rect(DX, DY + d1 + d2, DETAIL_SECTION_W, d3, C_NAVY, C_BLACK, sw=0.8),
        _rect(DX, DY + d1 + d2 + d3, DETAIL_SECTION_W, d4, l4_fill, C_BLACK, sw=0.8),
        *([
            _rect(DX, DY + d1 + d2 + d3, DETAIL_SECTION_W, d4,
                  "url(#clear-hatch)", "none"),
        ] if is_v2 else []),
        _rect(DX, DY, DETAIL_SECTION_W, DETAIL_H, "none", C_BLACK, sw=2),

        # Hatching on layers (light diagonal lines for engineering convention)
        # Ivory face hatching (light)
        '\n'.join([
            _line(DX + i * 8, DY, DX + min(i * 8 + d1, DETAIL_SECTION_W), DY + d1,
                  "#C8BFA8", 0.5)
            for i in range(0, DETAIL_SECTION_W // 8 + 2)
        ]),
        # Navy core hatching (light navy cross-hatch)
        '\n'.join([
            _line(DX, DY + d1 + d2 + i * 8,
                  DX + DETAIL_SECTION_W, DY + d1 + d2 + i * 8,
                  "#2A3D6E", 0.4)
            for i in range(0, int(d3 / 8) + 1)
        ]),

        # Layer dimension callouts (right side of detail)
        _dim_line_v(DY, DY + d1,
                    DX + DETAIL_SECTION_W + 34, f"{LAYER_1_MM}mm", ext_len=12, text_size=10),
        _dim_line_v(DY + d1, DY + d1 + d2,
                    DX + DETAIL_SECTION_W + 34, f"{LAYER_2_MM}mm", ext_len=12, text_size=10),
        _dim_line_v(DY + d1 + d2, DY + d1 + d2 + d3,
                    DX + DETAIL_SECTION_W + 34, f"{LAYER_3_MM}mm", ext_len=12, text_size=10),
        _dim_line_v(DY + d1 + d2 + d3, DY + DETAIL_H,
                    DX + DETAIL_SECTION_W + 34, f"{LAYER_4_MM}mm", ext_len=12, text_size=10),

        # Material labels — right of dim callouts (no left-side leaders to avoid view overlap)
        *[
            _text(DX + DETAIL_SECTION_W + 56, y + 4, label, size=9, fill=C_GRAY, anchor="start")
            for y, label in [
                (DY + d1 // 2,                   "L1: IVORY ACRYLIC"),
                (DY + d1 + d2 // 2,              "L2: GOLD HAIRLINE"),
                (DY + d1 + d2 + d3 // 2,         "L3: LAPIS NAVY CORE"),
                (DY + d1 + d2 + d3 + d4 // 2,    l4_label),
            ]
        ],

        # ════════════════════════════════════════════════════════════════════
        # SPECIFICATIONS TABLE (right panel, below layer detail)
        # ════════════════════════════════════════════════════════════════════
        _text(SPEC_X + SPEC_W // 2, SPEC_Y - 8,
              "MATERIAL &amp; PROCESS SPECIFICATIONS",
              size=11, weight="bold", fill=C_BLACK, anchor="middle"),

        # Spec rows
        *[
            (
                _rect(SPEC_X, SPEC_Y + 2 + i * SPEC_ROW_H, SPEC_W, SPEC_ROW_H - 1,
                      "#F0EFE8" if i % 2 == 0 else C_BGPAPER, C_LIGHTGRAY, sw=0.4)
                + "\n" +
                _text(SPEC_X + 6, SPEC_Y + 13 + i * SPEC_ROW_H,
                      label, size=9, fill=C_GRAY, anchor="start")
                + "\n" +
                _text(SPEC_COL2, SPEC_Y + 13 + i * SPEC_ROW_H,
                      value, size=9, fill=C_BLACK, anchor="start", weight="bold")
            )
            for i, (label, value) in enumerate([
                ("Material",              "Four-layer cast acrylic (PMMA)"),
                ("Overall dimensions",    f"{TILE_W_MM} × {TILE_H_MM} × {TILE_D_MM} mm"),
                ("Dimensional tolerance", f"±{TOL_MM} mm all faces"),
                ("Target weight",         f"{WEIGHT_G_MIN}–{WEIGHT_G_MAX} g per tile"),
                ("Quantity per set",      "152 tiles"),
                ("Layer 1 (face)",        f"Ivory/cream, {LAYER_1_MM} mm — Pantone ~9183 C"),
                ("Layer 2",              f"Metallic gold, {LAYER_2_MM} mm — Pantone ~874 C"),
                ("Layer 3 (core)",       f"Lapis navy, {LAYER_3_MM} mm — Pantone ~289 C"),
                ("Layer 4 (back)",       l4_spec),
                ("Back face appearance",  l4_back_note),
                ("Face surface finish",  "Mirror polished, Ra ≤ 0.4 μm (all 6 faces)"),
                ("UV print surface",     "Face (L1): must accept UV inkjet, zero texture"),
                ("Laser engrave",        "Face (L1): compatible with UV cold laser"),
                ("Edge visibility",      "All 4 layers visible on both 23mm edges"),
            ])
        ],

        # ════════════════════════════════════════════════════════════════════
        # TITLE BLOCK
        # ════════════════════════════════════════════════════════════════════
        # Variant badge (top-right corner of title block)
        _rect(TB_X + TB_W - 116, TB_Y - 26, 116, 20, C_NAVY, "none"),
        _text(TB_X + TB_W - 58, TB_Y - 11,
              dwg_number, size=9, fill="#FFFFFF", weight="bold"),

        _rect(TB_X, TB_Y, TB_W, TB_H, C_TITLE_BG, C_BLACK, sw=1.5),

        # Title block inner dividers
        _line(TB_X, TB_Y + 24, TB_X + TB_W, TB_Y + 24, C_BLACK, sw=0.8),
        _line(TB_X, TB_Y + 44, TB_X + TB_W, TB_Y + 44, C_BLACK, sw=0.5),
        _line(TB_X, TB_Y + 64, TB_X + TB_W, TB_Y + 64, C_BLACK, sw=0.5),
        _line(TB_X, TB_Y + 84, TB_X + TB_W, TB_Y + 84, C_BLACK, sw=0.5),
        _line(TB_X, TB_Y + 104, TB_X + TB_W, TB_Y + 104, C_BLACK, sw=0.5),
        _line(TB_X + 190, TB_Y + 24, TB_X + 190, TB_Y + TB_H, C_BLACK, sw=0.5),
        _line(TB_X + 360, TB_Y + 24, TB_X + 360, TB_Y + TB_H, C_BLACK, sw=0.5),

        _text(TB_X + TB_W // 2, TB_Y + 17,
              "MAHARAJONG BLANK TILE — 4-LAYER ACRYLIC",
              size=12, weight="bold", fill=C_BLACK),

        # Row labels
        *[
            _text(TB_X + ox + 5, TB_Y + oy + 8, label,
                  size=7, fill=C_GRAY, anchor="start")
            for (ox, oy, label) in [
                (0,   24, "COMPONENT"),   (190, 24, "DWG No."),       (360, 24, "REV"),
                (0,   44, "PROJECT"),     (190, 44, "SCALE"),          (360, 44, "UNITS"),
                (0,   64, "PREPARED BY"), (190, 64, "DATE"),           (360, 64, "SHEET"),
                (0,   84, "SUPPLIER: CONFIRM WEIGHT &amp; PANTONE BEFORE PRODUCTION"),
            ]
        ],

        # Row values
        *[
            _text(TB_X + ox + 5, TB_Y + oy + 20, value,
                  size=9, fill=C_BLACK, anchor="start", weight="bold")
            for (ox, oy, value) in [
                (0,   24, "Blank Tile (4-Layer Acrylic)"), (190, 24, dwg_number), (360, 24, "A"),
                (0,   44, "Maharajong"),                   (190, 44, "1:1 (main)"),  (360, 44, "mm"),
                (0,   64, "ccwells@gmail.com"),            (190, 64, "2026-07-12"), (360, 64, "1/1"),
            ]
        ],

        # ── Notes box (bottom-left, narrower than right-panel) ──────────────────
        _rect(20, FOOTER_Y, TB_X - 26, FOOTER_H, C_TITLE_BG, C_BLACK, sw=1),
        _text(28, FOOTER_Y + 14, "GENERAL NOTES:", size=9, weight="bold",
              fill=C_BLACK, anchor="start"),
        *[
            _text(28, FOOTER_Y + 27 + i * 16, note, size=8, fill=C_GRAY, anchor="start")
            for i, note in enumerate(
                [
                    "1. All dims in mm. Tolerances \u00b10.2mm unless noted.",
                    "2. All faces mirror-polished (Ra \u2264 0.4\u03bcm). Zero orange-peel.",
                    "3. Layer 1 face must accept UV inkjet without priming.",
                    "4. Gold hairline (L2) visible on both 23mm short edges.",
                    "5. L1\u2013L3 Pantone-matched; supplier submits chip for approval.",
                    "6. L4 CRYSTAL CLEAR — water-white, zero haze. No buffing on clear face.",
                    "7. QC: per-tile back-face clarity check — navy core uniform, no milky patches.",
                    "8. Weight 16\u201319g/tile. Advise if ballast fill needed.",
                    "9. 20-tile prototype required before production MOQ commitment.",
                ] if is_v2 else [
                    "1. All dims in mm. Tolerances \u00b10.2mm unless noted.",
                    "2. All faces mirror-polished (Ra \u2264 0.4\u03bcm). Zero orange-peel.",
                    "3. Layer 1 face must accept UV inkjet without priming.",
                    "4. Gold hairline (L2) visible on both 23mm short edges.",
                    "5. All layers Pantone-matched; supplier submits colour chip for approval.",
                    "6. Weight 16\u201319g/tile. Advise if ballast fill/drill needed.",
                    "7. 20-tile prototype required before production MOQ commitment.",
                ]
            )
        ],

        '</svg>',
    ]

    return "\n".join(svg_parts)


# ---------------------------------------------------------------------------
# Grok rendered image
# ---------------------------------------------------------------------------

# View-specific prompts — one Grok call per view for maximum accuracy.
# Multi-view composite rendered later in Python (not by Grok).

def get_view_prompts(variant: str) -> dict:
    """Return {view_name: prompt} for top, side, and back views."""
    is_v2 = (variant == "variant-02")

    base = (
        "Photorealistic studio product macro photography. "
        "Single blank mahjong tile, polished cast acrylic, no artwork. "
        "Pure white background, soft studio lighting, sharp focus throughout. "
        "No text, no labels, no annotations. No border or frame around the image."
    )

    top = (
        f"{base} "
        "CAMERA DIRECTLY OVERHEAD, looking straight down at the tile face (top view). "
        "The tile lies flat. Face surface is a single uninterrupted warm ivory cream "
        "(#F5EDD8), highly polished mirror-smooth acrylic. "
        "Tile is 32mm wide × 23mm tall — a portrait-ish rectangle. "
        "Soft specular highlight from overhead studio light. Very soft drop shadow at edges. "
        "The tile fills most of the frame, centred on white."
    )

    if is_v2:
        back = (
            f"{base} "
            "CAMERA DIRECTLY OVERHEAD, looking straight down at the tile back face (bottom view). "
            "The tile lies flat, back face up. "
            "Back surface appears deep lapis navy blue (#1C2E5E) — "
            "this is the navy acrylic core seen through a crystal-clear 3mm transparent acrylic top layer. "
            "The colour is rich, deep, dark navy with a subtle glossy depth and slight translucency. "
            "Tile is 32mm wide × 23mm tall. Soft specular highlight. Very soft drop shadow. "
            "The tile fills most of the frame, centred on white."
        )
    else:
        back = (
            f"{base} "
            "CAMERA DIRECTLY OVERHEAD, looking straight down at the tile back face (bottom view). "
            "The tile lies flat, back face up. "
            "Back surface is warm ivory cream (#E8DFC8), slightly darker than the face, "
            "highly polished acrylic. "
            "Tile is 32mm wide × 23mm tall. Soft specular highlight. Very soft drop shadow. "
            "The tile fills most of the frame, centred on white."
        )

    if is_v2:
        back_band = (
            "4th band at the VERY BOTTOM: crystal-clear transparent acrylic, "
            "same height as the top ivory band. The navy is faintly visible through it "
            "as a dark lapis tint. This clear band is at the bottom only."
        )
    else:
        back_band = (
            "4th band at the VERY BOTTOM: warm ivory cream, "
            "same height as the top ivory band."
        )

    side = (
        f"{base} "
        "CAMERA PERFECTLY LEVEL with the tile edge, flat orthographic straight-on view, "
        "no perspective angle, no 3D foreshortening. "
        "Looking directly at the 32mm long edge of the tile from the side. "
        "The tile is 13mm tall in this view. "
        "PROPORTION IS CRITICAL — the tile is predominantly navy blue when viewed from the side. "
        "EXACTLY FOUR horizontal bands, strict order top to bottom: "
        "1st band (TOP): warm ivory cream — a NARROW band, less than one quarter of total height. "
        "2nd band: ONE single metallic gold hairline — extremely thin, "
        "barely a line, much thinner than the ivory top. THIS IS THE ONLY GOLD. "
        "3rd band: deep lapis navy blue — by far the TALLEST band, "
        "nearly half the total height, clearly the dominant element. "
        "The tile looks mostly navy from the side because this band is so wide. "
        f"{back_band} "
        "CRITICAL: the ivory top and ivory bottom are BOTH narrow — "
        "together they take less space than the navy alone. "
        "EXACTLY ONE gold stripe. NO gold between navy and the bottom band. "
        "Photorealistic polished acrylic, studio lighting."
    )

    return {"top": top, "side": side, "back": back}


def _grok_image(api_key: str, prompt: str, aspect: str = "1:1") -> bytes:
    payload = json.dumps({
        "model": "grok-imagine-image-quality",
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": aspect,
        "resolution": "2k",
    }).encode()
    req = urllib.request.Request(
        "https://api.x.ai/v1/images/generations",
        data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    return base64.b64decode(body["data"][0]["b64_json"])


def composite_views(view_bytes: dict) -> bytes:
    """Stitch top / side / back renders into one landscape image using Pillow."""
    import subprocess, tempfile, importlib

    # Find a Python with Pillow
    pil = None
    for py in [sys.executable, "python3.10", "python3.11", "python3"]:
        try:
            r = subprocess.run([py, "-c", "from PIL import Image; print('ok')"],
                               capture_output=True, timeout=5)
            if r.returncode == 0:
                pil = py
                break
        except FileNotFoundError:
            continue
    if pil is None:
        raise RuntimeError("Pillow not found. Run: python3.10 -m pip install Pillow")

    # Write view images to temp files, composite via subprocess
    import os
    tmp = tempfile.mkdtemp()
    for name, data in view_bytes.items():
        Path(tmp, f"{name}.png").write_bytes(data)

    out = Path(tmp, "composite.png")
    script = f"""
import io
from pathlib import Path
from PIL import Image, ImageDraw

tmp = Path({repr(tmp)})
out = Path({repr(str(out))})

PANEL_H  = 1200   # px, height each panel is scaled to
GAP      = 60     # px between panels
PAD      = 80     # px outer padding
LABEL_H  = 72     # px for label area below each panel
BG       = (250, 250, 248)
FG       = (90, 90, 90)

views = []
for name, label in [("top", "TOP"), ("side", "SIDE"), ("back", "BACK")]:
    img = Image.open(tmp / f"{{name}}.png").convert("RGB")
    scale = PANEL_H / img.height
    img = img.resize((int(img.width * scale), PANEL_H), Image.LANCZOS)
    views.append((img, label))

total_w = PAD * 2 + sum(v.width for v, _ in views) + GAP * (len(views) - 1)
total_h = PAD + PANEL_H + LABEL_H + PAD

canvas = Image.new("RGB", (total_w, total_h), BG)
draw   = ImageDraw.Draw(canvas)

x = PAD
for img, label in views:
    canvas.paste(img, (x, PAD))
    draw.text((x + img.width // 2, PAD + PANEL_H + LABEL_H // 2),
              label, fill=FG, anchor="mm")
    x += img.width + GAP

canvas.save(str(out), "PNG")
print(f"composite: {{total_w}}x{{total_h}}")
"""
    r = subprocess.run([pil, "-c", script], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    print(f"   ({r.stdout.strip()})", end="", flush=True)
    data = out.read_bytes()
    # cleanup
    for f in Path(tmp).iterdir():
        f.unlink()
    os.rmdir(tmp)
    return data


def generate_rendered_image(api_key: str, variant: str = "variant-01") -> bytes:
    """Generate top/side/back views separately then composite them."""
    prompts = get_view_prompts(variant)
    view_bytes = {}
    for view, prompt in prompts.items():
        aspect = "16:9" if view == "side" else "1:1"
        print(f"\n   [{view}]", end=" ", flush=True)
        view_bytes[view] = _grok_image(api_key, prompt, aspect=aspect)
    print("\n   compositing", end="", flush=True)
    return composite_views(view_bytes)


def render_svg_to_png(svg_path, out_path, width=1100, height=850):
    """Render the SVG engineering drawing to PNG via headless Chromium.
    Produces a pixel-accurate rasterisation — correct layer proportions,
    exact dimensions, no AI hallucination.
    Falls back to python3.11 subprocess if playwright isn’t on the current interpreter."""
    import subprocess, tempfile
    from pathlib import Path
    svg_path = Path(svg_path)
    out_path  = Path(out_path)

    # Try importing directly first
    try:
        from playwright.sync_api import sync_playwright
        _run_playwright_inline(svg_path, out_path, width, height)
        return
    except ImportError:
        pass

    # Fall back: find a Python that has playwright and run as subprocess
    for py in ["python3.11", "python3.10", "python3.13", "python3"]:
        try:
            check = subprocess.run([py, "-c", "import playwright"],
                                   capture_output=True)
            if check.returncode != 0:
                continue
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                            delete=False) as f:
                f.write(_PLAYWRIGHT_SCRIPT)
                script = f.name
            result = subprocess.run(
                [py, script,
                 str(svg_path), str(out_path), str(width), str(height)],
                capture_output=True, text=True, timeout=60,
            )
            Path(script).unlink(missing_ok=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr[-400:])
            return
        except FileNotFoundError:
            continue
    raise RuntimeError(
        "playwright not found on any Python. Run: "
        "python3.11 -m pip install playwright && python3.11 -m playwright install chromium"
    )


def _run_playwright_inline(svg_path, out_path, width, height):
    import textwrap
    from playwright.sync_api import sync_playwright
    html = textwrap.dedent(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>body{{margin:0;padding:0;background:#fff}}</style></head>
<body>{svg_path.read_text()}</body></html>""")
    tmp = svg_path.parent / "_tmp_render.html"
    tmp.write_text(html)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"file://{tmp}")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(800)
            page.screenshot(path=str(out_path),
                            clip={"x":0,"y":0,"width":width,"height":height},
                            timeout=30000)
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)



# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Maharajong blank tile manufacturer spec sheet assets"
    )
    parser.add_argument("--svg-only", action="store_true",
                        help="Generate SVG technical drawing only (no API call)")
    parser.add_argument("--img-only", action="store_true",
                        help="Generate Grok rendered image only (no SVG)")
    parser.add_argument("--png-only", action="store_true",
                        help="Render SVG → PNG via Playwright/Chromium (exact proportions, no API call)")
    parser.add_argument("--variant", default=DEFAULT_VARIANT,
                        help=f"Tile variant folder to write outputs into (default: {DEFAULT_VARIANT})")
    args = parser.parse_args()

    out_dir = Path(__file__).parent / args.variant / "manufacturer-docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── SVG technical drawing ────────────────────────────────────────────────
    svg_path = out_dir / "tile-blank-technical-drawing.svg"
    if not args.img_only and not args.png_only:
        print("Generating SVG technical drawing...", end=" ", flush=True)
        svg_content = generate_svg(variant=args.variant)
        svg_path.write_text(svg_content, encoding="utf-8")
        print(f"OK \u2192 {svg_path}")

    # ── Playwright PNG (pixel-accurate rasterisation of the SVG) ───────────
    if args.png_only or (not args.img_only and not args.svg_only):
        png_path = out_dir / "tile-blank-technical-drawing.png"
        print("Rendering SVG \u2192 PNG via Chromium...", end=" ", flush=True)
        try:
            render_svg_to_png(svg_path, png_path)
            print(f"OK ({png_path.stat().st_size // 1024} KB) \u2192 {png_path}")
        except Exception as e:
            print(f"SKIP ({e})")
        if args.png_only:
            return

    # ── Grok rendered image ──────────────────────────────────────────────────
    if not args.svg_only:
        api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
        if not api_key:
            print("ERROR: Set GROK_API_KEY or XAI_API_KEY to generate the rendered image.",
                  file=sys.stderr)
            if args.img_only:
                sys.exit(1)
            else:
                print("Skipping rendered image (no API key).")
                return

        img_path = out_dir / "tile-blank-spec-sheet-rendered.png"
        print("Generating Grok rendered spec sheet image...", end=" ", flush=True)
        try:
            img_bytes = generate_rendered_image(api_key, variant=args.variant)
            img_path.write_bytes(img_bytes)
            size_kb = len(img_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB) → {img_path}")
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code}): {body[:200]}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
