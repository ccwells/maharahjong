# Tile Spec Sheet — SVG Layout Reference

Generator script: `design/generate_tile_spec_sheet.py`

## Quick commands

```bash
# SVG only (no API, no Chromium)
python3 design/generate_tile_spec_sheet.py --svg-only --variant variant-01

# PNG rasterisation of SVG via Chromium (pixel-accurate, no AI)
python3 design/generate_tile_spec_sheet.py --png-only --variant variant-01

# Grok 3D rendered image only (marketing impression)
python3 design/generate_tile_spec_sheet.py --img-only --variant variant-01

# Full pipeline: SVG + Chromium PNG + Grok render
python3 design/generate_tile_spec_sheet.py --variant variant-01

# Regenerate all variants
for v in variant-01 variant-02; do
  python3 design/generate_tile_spec_sheet.py --variant $v
done
```

Outputs go to `design/<variant>/manufacturer-docs/`:
- `tile-blank-technical-drawing.svg` — engineering drawing source (Letter landscape, 11×8.5in)
- `tile-blank-technical-drawing.png` — **pixel-accurate** rasterisation via Playwright/Chromium
- `tile-blank-spec-sheet-rendered.png` — Grok 3D perspective render (marketing impression only)

**Use the Chromium PNG for supplier submissions** — it has mathematically correct layer
proportions. The Grok render is approximate and suitable for marketing materials only.

Playwright/Chromium must be installed to generate the PNG:
```bash
python3.11 -m pip install playwright
python3.11 -m playwright install chromium
```

---

## Canvas and print dimensions

| Property | Value |
|----------|-------|
| SVG `width` / `height` | `11in` / `8.5in` (Letter landscape) |
| ViewBox | `0 0 1100 850` (100 units per inch) |
| Working units | px — 1px = 0.01in = 0.254mm |
| Margin | 20px all sides |

---

## Scale system

Two scales are used simultaneously. Both are defined at the top of `generate_svg()`:

| Variable | Value | Used for |
|----------|-------|----------|
| `SC` | `8 px/mm` | Main orthographic views (Views A, B, C) — 1:1 effective scale |
| `SC2` | `16 px/mm` | Detail D layer cross-section — 2:1 scale |

Derived tile dimensions (computed automatically from `SC`/`SC2`):

| Variable | Formula | Value at SC=8 |
|----------|---------|---------------|
| `W` | `TILE_W_MM × SC` | 256 px (32mm) |
| `H` | `TILE_H_MM × SC` | 184 px (23mm) |
| `D` | `TILE_D_MM × SC` | 104 px (13mm) |
| `l1..l4` | `LAYER_n_MM × SC` | 24 / 8 / 48 / 24 px |
| `d1..d4` | `LAYER_n_MM × SC2` | 48 / 16 / 96 / 48 px |
| `DETAIL_H` | `TILE_D_MM × SC2` | 208 px |

---

## Layout zones

```
┌──────────────────────────────────────────────────────────────┐
│  HEADER  —  title, variant label, drawing number    y: 0–100 │
├───────────────────────────────┬──────────────────────────────┤
│  LEFT PANEL  x: 20–614        │  RIGHT PANEL  x: 614–1080    │
│                               │                              │
│  View A  face (32×23mm)       │  Detail D  layer cross-sec.  │
│  View B  long edge (32×13mm)  │  Spec table (14 rows)        │
│  View C  short edge (23×13mm) │                              │
│                               │                 y: 100–698   │
├───────────────────────────────┴──────────────────────────────┤
│  FOOTER  —  general notes + title block             y: 700–  │
│  Notes box  x: 20–484  │  Title block  x: 510–1080           │
└──────────────────────────────────────────────────────────────┘
```

---

## Key position variables

All defined near the top of `generate_svg()`:

### Left panel

| Variable | Value | Description |
|----------|-------|-------------|
| `VX` | `70` | Left edge of face/edge views |
| `VY` | `115` | Top of face view (View A) |
| `FX, FY` | `VX, VY` | Face view origin |
| `EX, EY` | `VX, FY+H+85` | Long-edge view origin |
| `SEX, SEY` | `EX+W+60, EY` | Short-edge view origin |

### Right panel

| Variable | Value | Description |
|----------|-------|-------------|
| `DIVIDER_X` | `614` | Vertical divider between panels |
| `DX` | `640` | Left edge of Detail D diagram |
| `DY` | `VY` | Top of Detail D (aligned with left panel) |
| `DETAIL_SECTION_W` | `155` | Width of Detail D diagram |
| `DETAIL_H` | `208` | Height of Detail D (`TILE_D_MM × SC2`) |

### Spec table

| Variable | Formula | Value |
|----------|---------|-------|
| `SPEC_X` | `DX - 4` | Left edge |
| `SPEC_Y` | `DY + DETAIL_H + 36` | Top (below Detail D) |
| `SPEC_W` | `CANVAS_W - SPEC_X - 22` | Width (to right margin) |
| `SPEC_ROW_H` | `19` | Row height (px) |
| `SPEC_COL2` | `SPEC_X + 195` | Value column x position |

### Footer

| Variable | Value | Description |
|----------|-------|-------------|
| `FOOTER_Y` | `700` | Top of footer strip |
| `FOOTER_H` | `CANVAS_H - FOOTER_Y - 18` | Footer height |
| `TB_X` | `510` | Title block left edge |
| `TB_Y` | `FOOTER_Y` | Title block top |
| `TB_W` | `CANVAS_W - TB_X - 20` | Title block width |
| `TB_H` | `FOOTER_H` | Title block height |
| Notes box | `x=20, w=TB_X-26` | Left of title block |

---

## Spec table vertical budget

With current values:
- `SPEC_Y` = 115 + 208 + 36 = **359**
- 14 rows × 19px = 266px → `SPEC_Y + 266` = **625**
- `FOOTER_Y` = **700**
- Clearance: 700 − 625 = **75 px** ← comfortable

For a new variant with more spec rows:
- Each extra row costs 19px
- Budget for extra rows: `(FOOTER_Y - SPEC_Y - 20) / SPEC_ROW_H` ≈ **35 rows max**

---

## Adding a new variant

1. **Create the variant folder**:
   ```bash
   mkdir -p design/variant-03
   ```

2. **Copy and edit the spec files** from the closest existing variant:
   ```bash
   cp design/variant-02/materials-spec.md design/variant-03/materials-spec.md
   cp design/variant-02/tile-blanks-spec.md design/variant-03/tile-blanks-spec.md
   ```

3. **Add the variant to `generate_svg()`** in `generate_tile_spec_sheet.py`:
   - Add `is_v3 = (variant == "variant-03")` near the other `is_v2` flags
   - Add layer fill/label/spec/back-note overrides following the existing pattern
   - Add a `dwg_number` entry: `"MJ-TILE-BLK-003"`
   - Add a `variant_label` entry

4. **Add a Grok prompt** in `get_rendered_prompt(variant)`:
   ```python
   if variant == "variant-03":
       return "...describe the new visual..."
   ```

5. **Generate**:
   ```bash
   python3 design/generate_tile_spec_sheet.py --variant variant-03
   ```

6. **Open in Safari / browser** to review the SVG before sending to suppliers.

7. **Validate XML** (catches any unescaped `&` or malformed tags):
   ```bash
   xmllint --noout design/variant-03/manufacturer-docs/tile-blank-technical-drawing.svg
   ```

---

## Common pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Safari XML error | Unescaped `&` in text content | Use `&amp;` in all SVG text strings |
| Spec table overflows footer | Too many rows or large `SPEC_ROW_H` | Reduce `SPEC_ROW_H` or increase `FOOTER_Y` |
| View C overlaps divider | `SEX + TILE_H_MM*SC > DIVIDER_X` | Increase `DIVIDER_X` or reduce `SEX` |
| Right-panel labels overlap | `DX + DETAIL_SECTION_W + 56 + label_width > CANVAS_W - 20` | Shorten label text or reduce `DETAIL_SECTION_W` |
| Leader text off-canvas | SC2 too large, DETAIL_H too tall | Reduce SC2 |

---

## Variant registry

| Variant | Drawing No. | Layer stack | Status |
|---------|-------------|-------------|--------|
| variant-01 | MJ-TILE-BLK-001 | Ivory / Gold / Navy / **Ivory** | Confirmed spec |
| variant-02 | MJ-TILE-BLK-002 | Ivory / Gold / Navy / **Clear** | Design proposal |
