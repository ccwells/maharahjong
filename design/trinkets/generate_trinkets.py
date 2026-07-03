#!/usr/bin/env python3
"""Generate Maharajong trinkets & accessories product reference images using the xAI Grok Imagine API.

Uses GROK_API_KEY from the environment. No third-party dependencies required.

Generates two images:
  - trinkets-flatlay.png  — all tokens arranged together as a full set
  - trinkets-coins.png    — scoring coins close-up showing three denominations

Usage:
    python3 design/trinkets/generate_trinkets.py            # generate both images
    python3 design/trinkets/generate_trinkets.py --dry-run  # print prompts only
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.x.ai/v1/images/generations"
MODEL = "grok-imagine-image-quality"
TRINKETS_DIR = Path(__file__).parent

# Full set flat-lay — all token types in one product shot
FLATLAY_PROMPT = (
    "Premium product photography flat-lay of luxury Maharajong brass game tokens and markers, "
    "arranged neatly on deep navy/teal neoprene, soft diffused studio lighting with subtle shadows. "
    "All pieces in antique brass patina — warm aged gold-bronze, lightly brushed texture, "
    "matching the Maharajong dice. "
    ""
    "Top row: four square wind marker tokens (approx 16mm × 16mm × 4mm) with rounded corners. "
    "Each has a Devanagari character recessed and filled with deep teal enamel: पू (East), द (South), प (West), उ (North). "
    "Maharajong lotus-peacock logo recessed on the reverse of each marker. "
    ""
    "Center-left: one circular dealer token (approx 18mm diameter, 4mm thick) — slightly larger than the wind markers — "
    "with a peacock-feather eye motif on the front, teal enamel eye-spot in a gold surround, recessed. "
    ""
    "Center-right: one diamond/rhombus-shaped ready declaration token (approx 16mm across, 4mm thick) "
    "with a Sri Yantra sacred geometric motif on front — minimal gold on brass, no enamel fill. "
    ""
    "Bottom section: scoring coins in three sizes arranged in neat stacks by denomination — "
    "small coins (approx 14mm, teal enamel center), "
    "medium coins (approx 16mm, magenta-pink enamel center), "
    "large coins (approx 18mm, royal purple enamel center). "
    "Lotus-peacock logo visible on the face of front coins in each stack. "
    "Each stack shows 3–5 coins to convey quantity without obscuring design. "
    ""
    "All pieces show crisp recessed engravings with enamel fill. "
    "Overall aesthetic: premium Indian art deco game accessories, heavy brass craftsmanship, "
    "rich teal/magenta/purple enamel palette against antique gold-bronze brass. "
    "No text, no watermarks."
)

# Close-up of the three scoring coin denominations
COINS_PROMPT = (
    "Premium macro product photography of Maharajong scoring coins, "
    "three denominations displayed on deep navy/teal neoprene, "
    "soft diffused studio lighting, shallow depth of field. "
    "All coins solid brass with antique patina — warm aged gold-bronze, lightly brushed texture. "
    "Left: small coin (approx 14mm diameter) — teal enamel circle at center, "
    "Maharajong lotus-peacock logo engraved on face, raised edge. "
    "Center: medium coin (approx 16mm diameter) — magenta-pink enamel circle at center, same logo. "
    "Right: large coin (approx 18mm diameter) — royal purple enamel circle at center, same logo. "
    "Coins angled slightly to show edge thickness (approx 3mm). "
    "A few coins stacked behind each to show they are stackable game tokens. "
    "The enamel colors are vivid and jewel-like against the warm brass. "
    "Overall aesthetic: premium Indian-inspired game token, heavy brass, rich enamel. "
    "No text, no watermarks."
)

IMAGES: list[tuple[str, str, str]] = [
    ("trinkets-flatlay.png", FLATLAY_PROMPT, "1:1"),
    ("trinkets-coins.png", COINS_PROMPT, "4:3"),
]


def generate_image(prompt: str, api_key: str, aspect_ratio: str = "1:1") -> bytes:
    """Call xAI image generation API, return raw image bytes."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": aspect_ratio,
        "resolution": "2k",
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
    parser = argparse.ArgumentParser(description="Generate Maharajong trinkets design via xAI API")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling the API")
    args = parser.parse_args()

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: Set GROK_API_KEY or XAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        for filename, prompt, ratio in IMAGES:
            print(f"[DRY RUN] {filename} ({ratio}):\n")
            print(prompt)
            print()
        return

    print(f"Generating {len(IMAGES)} trinkets image(s)...\n")

    for filename, prompt, ratio in IMAGES:
        out_path = TRINKETS_DIR / filename
        print(f"  Generating: {filename} ({ratio}) ...", end=" ", flush=True)

        try:
            image_bytes = generate_image(prompt, api_key, aspect_ratio=ratio)
            out_path.write_bytes(image_bytes)
            size_kb = len(image_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code})")
            print(f"      {error_body[:200]}")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nDone! Output: {TRINKETS_DIR}/")


if __name__ == "__main__":
    main()
