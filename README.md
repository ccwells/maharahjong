# Project Maharahjong 🀄🇮🇳

**Indian Fusion Mahjong** - Premium game blending Chinese, Japanese, American Mahjong with rangoli artistry, Vedic depth, and Rummy strategy.

## Quick Start
1. Clone: `git clone https://github.com/ccwells/maharahjong.git`
2. Explore `rules/gameplay-rules.md` for gameplay.
3. Check `/design/` for visuals.

## Tile Design Generation
Tile artwork is generated via the xAI Grok Imagine API. Requires `GROK_API_KEY` in your environment.

```bash
# Generate all 51 unique tile designs
python3 design/tiles/generate_tiles.py

# Generate a single category
python3 design/tiles/generate_tiles.py --category suit-lotus

# Available categories:
#   suit-lotus, suit-peacock, suit-vedic,
#   honors-wind, honors-deity,
#   bonus-festival, bonus-chakra, tile-back

# Preview prompts without calling the API
python3 design/tiles/generate_tiles.py --dry-run

# Skip tiles that already exist
python3 design/tiles/generate_tiles.py --skip-existing
```

After generating, crop the tiles to the exact 32×23mm tile-face proportion for printing (outputs to `design/tiles/print-ready/`, originals preserved):

```bash
# Uses Pillow if installed, otherwise falls back to macOS `sips`
python3 design/tiles/fix_aspect_ratio.py

# Preview the planned crops without writing files
python3 design/tiles/fix_aspect_ratio.py --dry-run
```

For UV printing onto pre-coloured tile blanks, export versions with the ivory/cream background replaced by alpha transparency (outputs to `design/tiles/transparent/`, print-ready originals preserved):

```bash
# Requires Pillow (pip install Pillow)
python3.10 design/tiles/export_transparent.py

# Preview the list of tiles without writing files
python3.10 design/tiles/export_transparent.py --dry-run

# Tune background removal if needed
python3.10 design/tiles/export_transparent.py --rel-tolerance 30 --abs-tolerance 70
```

See `design/tiles/tile-design-spec.md` for the full art direction and prompt details.

## Mat Design Generation
```bash
# Generate mat design variants
python3 design/mat/generate_mat.py --variants 3
```

## Project Structure
- `rules/gameplay-rules.md` — Game rules v0.1
- `design/tiles/` — 51 tile images + generation script + art spec
  - `print-ready/` — aspect-ratio corrected PNGs (32:23) for UV printing
  - `transparent/` — transparent-background PNGs for pre-coloured tile blanks
- `design/mat/` — Playing mat design + generation script
- `design/racks/` — Tile rack design spec + 3 reference images
- `design/dice/` — Dice design spec + 3 reference images
- `design/trinkets/` — Trinkets & accessories spec + flat-lay and coin close-up
- `design/marketing/` — Social media teaser images
- `design/tile-blanks-spec.md` — Tile blank sourcing (3 suppliers)
- `production/` — Equipment specs (xTool laser, eufyMake printer) + production audit

See `PROJECT-PLAN.md` for full task tracking and current status.

See Google Drive for high-res files: https://drive.google.com/drive/folders/1BGU8itF4Ah9BdL0AtKzQUNMFCiG10iSm
