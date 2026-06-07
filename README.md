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

## Artifacts
All mood boards, tile designs, rules, and plans are here.

See Google Drive for high-res files: https://drive.google.com/drive/folders/1BGU8itF4Ah9BdL0AtKzQUNMFCiG10iSm
