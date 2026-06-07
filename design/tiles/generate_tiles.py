#!/usr/bin/env python3
"""Generate Maharahjong tile images using the xAI Grok Imagine API.

Uses GROK_API_KEY from the environment. No third-party dependencies required.
Generates 51 unique tile designs (the game's 152 tiles are copies of these).

Usage:
    python3 design/tiles/generate_tiles.py               # generate all tiles
    python3 design/tiles/generate_tiles.py --category suit-lotus  # one category
    python3 design/tiles/generate_tiles.py --dry-run      # print prompts only
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.x.ai/v1/images/generations"
MODEL = "grok-imagine-image-quality"
ASPECT_RATIO = "3:4"  # closest to 32×23mm tile face (1.39:1)
RESOLUTION = "2k"
TILES_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Shared style fragments
# ---------------------------------------------------------------------------
TILE_BASE = (
    "premium mahjong tile face design, ivory/cream tile background, "
    "thin gold border, intricate but readable at small size"
)
RANGOLI_STYLE = "Indian rangoli-inspired style, clean vector line art with rich detail"
TEMPLE_STYLE = "Indian Hoysala/Chola temple sculpture style, clean vector line art with rich detail"

# ---------------------------------------------------------------------------
# Tile definitions — each is (filename, prompt)
# ---------------------------------------------------------------------------

def _lotus(n: int, desc: str) -> tuple[str, str]:
    prompt = (
        f"{TILE_BASE}, {n} lotus {desc}, magenta-pink and gold color scheme, "
        f"{RANGOLI_STYLE}, small decorative numeral \"{n}\" in top-left corner, "
        f"Hoysala temple meets modern board game aesthetic, no text other than the numeral"
    )
    return (f"suit-lotus/lotus-{n}.png", prompt)


def _peacock(n: int, desc: str) -> tuple[str, str]:
    prompt = (
        f"{TILE_BASE}, {n} peacock feather(s) {desc}, "
        f"teal and iridescent blue-green with gold accents, {RANGOLI_STYLE}, "
        f"small decorative numeral \"{n}\" in top-left corner, "
        f"inspired by Indian peacock rangoli art and henna patterns, no text other than the numeral"
    )
    return (f"suit-peacock/peacock-{n}.png", prompt)


def _vedic(n: int, symbol: str, desc: str) -> tuple[str, str]:
    prompt = (
        f"{TILE_BASE}, {symbol}: {desc}, royal purple and gold color scheme, "
        f"Indian temple carving meets rangoli stencil style, clean vector line art with rich detail, "
        f"small decorative numeral \"{n}\" in top-left corner, "
        f"sacred Hindu/Vedic iconography rendered respectfully and beautifully, no text other than the numeral"
    )
    return (f"suit-vedic/vedic-{n}.png", prompt)


def _wind(direction: str, char: str, desc: str) -> tuple[str, str]:
    slug = direction.lower().split()[0]
    prompt = (
        f"{TILE_BASE}, Wind tile \"{direction}\": {desc}, "
        f"saffron orange-gold and dark teal color scheme, Indian temple and landscape art style, "
        f"clean vector line art with rich detail, "
        f"Devanagari character \"{char}\" in top-left corner, no other text"
    )
    return (f"honors/wind-{slug}.png", prompt)


def _deity(name: str, virtue: str, desc: str, colors: str) -> tuple[str, str]:
    slug = name.lower()
    prompt = (
        f"{TILE_BASE}, Deity tile \"{name}\" representing {virtue}: {desc}, "
        f"{colors}, {TEMPLE_STYLE}, "
        f"ornate gold border (thicker than suit tiles to denote honor status), "
        f"sacred iconography rendered with reverence and beauty, no text"
    )
    return (f"honors/deity-{slug}.png", prompt)


def _festival(name: str, desc: str, colors: str) -> tuple[str, str]:
    slug = name.lower().replace(" ", "-")
    prompt = (
        f"{TILE_BASE}, Rangoli bonus tile for {name}: {desc}, "
        f"{colors}, Indian rangoli mandala art style, "
        f"vibrant colored powder/flower petal texture feel, clean vector art with rich detail, "
        f"decorative scalloped gold border, "
        f"no numeral — tile is identified purely by its unique festival design, no text"
    )
    return (f"bonus-festival/festival-{slug}.png", prompt)


def _chakra(name: str, color: str, desc: str, syllable: str) -> tuple[str, str]:
    slug = name.lower().split()[0]
    prompt = (
        f"{TILE_BASE}, Chakra wild tile \"{name}\": {desc}, "
        f"{color} dominant with gold accents, "
        f"Indian sacred geometry and yantra style, clean vector line art, "
        f"thin iridescent/holographic-style border to distinguish as wild tile, "
        f"spiritual chakra symbolism rendered beautifully, no text other than the Sanskrit seed syllable \"{syllable}\""
    )
    return (f"bonus-chakra/chakra-{slug}.png", prompt)


# All 51 unique tile designs
TILES: dict[str, list[tuple[str, str]]] = {
    "suit-lotus": [
        _lotus(1, "single open lotus bloom viewed from above, layered petals radiating outward, gold-tipped edges, central seed pod visible"),
        _lotus(2, "two lotus buds side by side, partially open, on curved stems with a single leaf between them"),
        _lotus(3, "three lotus blooms in a triangular arrangement, varying stages of bloom (bud, half-open, full)"),
        _lotus(4, "four lotus blooms at compass points, connected by a circular vine/stem motif forming a rangoli-like frame"),
        _lotus(5, "five lotuses arranged in a dice-five pattern (quincunx), center lotus is full bloom, corners are buds, henna-style leaf fill between"),
        _lotus(6, "six petals radiating from a central point forming a hexagonal flower, each petal containing a smaller lotus motif"),
        _lotus(7, "seven lotuses cascading in an arc like floating on water, graduated sizes, small ripple lines beneath"),
        _lotus(8, "eight lotus petals in a mandala circle, alternating pink and gold, with a jewel center"),
        _lotus(9, "nine-petal grand lotus mandala filling the full tile face, most ornate, layered petals with henna-style interior detail, gold filigree"),
    ],
    "suit-peacock": [
        _peacock(1, "single upright peacock feather, full iridescent eye detail, teal-green-blue gradient, ornate quill base with gold filigree"),
        _peacock(2, "two feathers crossed in an X, eyes facing outward, gold quill crossing point"),
        _peacock(3, "three feathers fanned upward like a small crest, henna-style curl details on the barbs"),
        _peacock(4, "four feathers at compass points radiating from a central jewel, forming a cross/star motif"),
        _peacock(5, "five feather eyes arranged in a vertical stack like traditional bamboo tiles, connected by a decorative gold spine"),
        _peacock(6, "six feathers arranged in a circular fan, eye-spots forming an outer ring, inspired by the peacock's full display"),
        _peacock(7, "seven feathers in a sweeping arc, decreasing in size, paisley-influenced curves on the barbs"),
        _peacock(8, "eight feather eyes in two rows of four, arranged like a section of a peacock's full tail spread, geometric framing"),
        _peacock(9, "full peacock tail display filling the tile face, nine eye-spots visible amid cascading barbs, most elaborate design, rangoli peacock style"),
    ],
    "suit-vedic": [
        _vedic(1, "Om (ॐ)", "stylized Om symbol in gold on purple field, surrounded by radiating dots"),
        _vedic(2, "Diya (oil lamp)", "pair of lit diyas with flame, marigold petals scattered around base"),
        _vedic(3, "Trishula (trident)", "Shiva's trident ornately decorated with paisley fills and a small damaru drum"),
        _vedic(4, "Swastika (auspicious Hindu symbol)", "traditional clockwise swastika with four dots in quadrants, rangoli-style border"),
        _vedic(5, "Kalasha (sacred pot)", "overflowing ceremonial pot with mango leaves and coconut, gold filigree details"),
        _vedic(6, "Shankha (conch shell)", "sacred conch shell with spiral detail, emanating sound waves rendered as decorative arcs"),
        _vedic(7, "Chakra (wheel)", "Sudarshana-style discus/wheel with ornate spokes and a flaming rim"),
        _vedic(8, "Padma (lotus throne)", "lotus pedestal/throne viewed from the front, layered petals, temple-carving style"),
        _vedic(9, "Sri Yantra", "sacred geometric mandala with interlocking triangles and a bindu center, most complex design"),
    ],
    "honors-wind": [
        _wind("East (Purva)", "पू", "rising sun over a temple gopuram silhouette, rays radiating upward"),
        _wind("South (Dakshina)", "द", "lush tropical motif, banana leaf arch framing a Dravidian temple tower"),
        _wind("West (Paschima)", "प", "setting sun sinking into ocean waves, stylized like Rajasthani miniature painting water"),
        _wind("North (Uttara)", "उ", "snow-capped Himalayan peaks with prayer flags, stylized geometric mountain range"),
    ],
    "honors-deity": [
        _deity("Garuda", "Power", "Garuda in flight, half-eagle half-human, wings spread wide, Hoysala temple relief carving style", "ruby red and gold"),
        _deity("Nandi", "Devotion", "sacred bull Nandi seated in repose, decorated with garlands and a ceremonial cloth, temple sculpture style with ornate jewelry detail", "emerald green and gold"),
        _deity("Lotus", "Purity", "grand lotus emerging from water, fully open, glowing with divine light, pure white petals with pink tips and gold center on a deep teal water background", "white, pink, gold, deep teal"),
    ],
    "bonus-festival": [
        _festival("Diwali", "circular rangoli with diyas at compass points, marigold garland border, central flame", "orange, red, gold"),
        _festival("Holi", "splatter/powder burst rangoli, concentric rings of color radiating from center, playful and energetic", "pink, yellow, green, blue, purple"),
        _festival("Onam", "Pookalam-style floral carpet, concentric rings of different flower petals", "white, orange, yellow, green"),
        _festival("Navratri", "Garba dancer silhouettes circling a central lamp, rangoli border of dandiya sticks crossed", "red, gold, green"),
        _festival("Pongal", "overflowing rice pot at center, kolam-style geometric border, sugarcane stalks", "yellow, green, terracotta"),
        _festival("Raksha Bandhan", "ornate rakhi bracelet at center, surrounded by a mandala of protective motifs", "red, gold, purple"),
        _festival("Makar Sankranti", "colorful kites filling the tile in a diamond pattern, thin strings crossing, blue sky background", "multicolor kites on blue"),
        _festival("Ganesh Chaturthi", "Ganesha silhouette in the center of a modak-shaped rangoli frame, surrounded by laddu offerings", "orange, red, gold"),
    ],
    "bonus-chakra": [
        _chakra("Muladhara (Root)", "red", "four-petaled lotus with a downward triangle, square earth yantra at center", "लं"),
        _chakra("Svadhisthana (Sacral)", "orange", "six-petaled lotus with a crescent moon, water element motif", "वं"),
        _chakra("Manipura (Solar Plexus)", "yellow", "ten-petaled lotus with a downward triangle, fire element radiating energy", "रं"),
        _chakra("Anahata (Heart)", "green", "twelve-petaled lotus with two interlocking triangles (star shape), air element", "यं"),
        _chakra("Vishuddha (Throat)", "blue", "sixteen-petaled lotus with a circle and downward triangle, ether/space element", "हं"),
        _chakra("Ajna (Third Eye)", "indigo", "two large petals flanking a central circle, wisdom eye motif", "ॐ"),
        _chakra("Sahasrara (Crown)", "violet and white", "thousand-petaled lotus suggested by many fine radiating petals, golden bindu at center, most ethereal design", "ॐ"),
        _chakra("Universal Wild", "rainbow and gold", "all seven chakra colors in concentric rings, central golden spiral, ultimate wild card energy", "ॐ"),
    ],
    "tile-back": [
        ("tile-back/tile-back.png",
         f"{TILE_BASE}, tile BACK design (not a face), deep navy/teal background, "
         "centered Maharahjong logo: a stylized golden lotus-peacock hybrid motif — "
         "lotus base with peacock feather eye emerging from center — "
         "surrounded by a geometric rangoli border in gold filigree, "
         "Indian art deco fusion style, seamless repeating pattern of tiny rangoli dots "
         "in the background field, luxurious and premium feel, no text"),
    ],
}


def generate_image(prompt: str, api_key: str) -> bytes:
    """Call xAI image generation API, return raw image bytes."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": ASPECT_RATIO,
        "resolution": RESOLUTION,
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())

    b64_data = body["data"][0]["b64_json"]
    return base64.b64decode(b64_data)


def main():
    parser = argparse.ArgumentParser(description="Generate Maharahjong tile images via xAI API")
    parser.add_argument(
        "--category",
        choices=list(TILES.keys()) + ["all"],
        default="all",
        help="Which tile category to generate (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling the API")
    parser.add_argument("--skip-existing", action="store_true", help="Skip tiles that already have images")
    args = parser.parse_args()

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: Set GROK_API_KEY or XAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    categories = list(TILES.keys()) if args.category == "all" else [args.category]
    tiles_to_generate = []
    for cat in categories:
        tiles_to_generate.extend(TILES[cat])

    total = len(tiles_to_generate)
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Generating {total} unique tile designs\n")

    generated = 0
    skipped = 0
    failed = 0

    for i, (filename, prompt) in enumerate(tiles_to_generate, 1):
        out_path = TILES_DIR / filename
        tag = f"[{i}/{total}]"

        if args.skip_existing and out_path.exists():
            print(f"  {tag} SKIP (exists): {filename}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  {tag} {filename}")
            print(f"      {prompt[:120]}...\n")
            continue

        print(f"  {tag} Generating: {filename} ...", end=" ", flush=True)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            image_bytes = generate_image(prompt, api_key)
            out_path.write_bytes(image_bytes)
            size_kb = len(image_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB)")
            generated += 1
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code})")
            print(f"      {error_body[:200]}")
            failed += 1
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1

        # Rate limit: be gentle with the API
        if i < total:
            time.sleep(2)

    print(f"\nDone! Generated: {generated}, Skipped: {skipped}, Failed: {failed}")
    print(f"Output: {TILES_DIR}/")


if __name__ == "__main__":
    main()
