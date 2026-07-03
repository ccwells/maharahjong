#!/usr/bin/env python3
"""Generate Maharajong dice product reference images using the xAI Grok Imagine API.

Uses GROK_API_KEY from the environment. No third-party dependencies required.

Usage:
    python3 design/dice/generate_dice.py               # generate 3 variants
    python3 design/dice/generate_dice.py --variants 1  # single image
    python3 design/dice/generate_dice.py --dry-run     # print prompt only
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
DICE_DIR = Path(__file__).parent

DICE_PROMPT = (
    "Premium macro product photography of a pair of luxury antique brass mahjong dice, "
    "displayed on deep navy/teal neoprene, soft diffused studio lighting with subtle shadows. "
    "Two 16mm solid brass six-sided dice with rounded corners, visibly heavy — solid brass, no hollow core. "
    "Antique brass patina finish: warm aged gold-bronze tone, lightly brushed texture "
    "to reduce fingerprint visibility and add tactile character. "
    "Pips are small recessed lotus-bud engravings filled with deep teal enamel — "
    "the lotus bud sits cleanly in a shallow well. "
    "The 1-pip face features a single larger peacock-feather eye motif instead of a plain dot: "
    "an iridescent teal eye-spot in a golden surround, recessed and enamel-filled. "
    "Each face has a subtle recessed border line framing the pips, "
    "echoing the gold border treatment on the Maharajong tiles. "
    "One die is angled to show the 1-pip peacock-feather face prominently. "
    "The other die shows the 6-pip lotus-bud face. "
    "A tiny Maharajong lotus-peacock logo is engraved in one corner of the 6-pip face — subtle, not competing with the pips. "
    "The brass surface catches the light beautifully, showing craftsmanship and weight. "
    "Overall aesthetic: luxury Indian-inspired game accessory, warm antique brass on deep navy. "
    "No text, no watermarks."
)


def generate_image(prompt: str, api_key: str) -> bytes:
    """Call xAI image generation API, return raw image bytes."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": "1:1",
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
    parser = argparse.ArgumentParser(description="Generate Maharajong dice design via xAI API")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling the API")
    parser.add_argument("--variants", type=int, default=3, help="Number of design variants to generate (default: 3)")
    args = parser.parse_args()

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: Set GROK_API_KEY or XAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[DRY RUN] Dice design prompt:\n")
        print(DICE_PROMPT)
        return

    print(f"Generating {args.variants} dice design variant(s)...\n")

    for i in range(1, args.variants + 1):
        out_path = DICE_DIR / f"dice-design-v{i}.png"
        print(f"  [{i}/{args.variants}] Generating: {out_path.name} ...", end=" ", flush=True)

        try:
            image_bytes = generate_image(DICE_PROMPT, api_key)
            out_path.write_bytes(image_bytes)
            size_kb = len(image_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code})")
            print(f"      {error_body[:200]}")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nDone! Output: {DICE_DIR}/")


if __name__ == "__main__":
    main()
