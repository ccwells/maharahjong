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

See `design/tiles/tile-design-spec.md` for the full art direction and prompt details.

## Mat Design Generation
```bash
# Generate mat design variants
python3 design/mat/generate_mat.py --variants 3
```

## Project Structure
- `rules/gameplay-rules.md` — Game rules v0.1
- `design/tiles/` — 51 tile images + generation script + art spec
- `design/mat/` — Playing mat design + generation script
- `design/racks/` — Tile rack design spec
- `design/dice/` — Dice design spec (antique brass)
- `design/trinkets/` — Trinkets & accessories spec (brass tokens)
- `design/marketing/` — Social media teaser images
- `design/tile-blanks-spec.md` — Tile blank sourcing (3 suppliers)
- `production/` — Equipment specs (xTool laser, eufyMake printer) + production audit

See `PROJECT-PLAN.md` for full task tracking and current status.

See Google Drive for high-res files: https://drive.google.com/drive/folders/1BGU8itF4Ah9BdL0AtKzQUNMFCiG10iSm
