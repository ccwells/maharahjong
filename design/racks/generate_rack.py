#!/usr/bin/env python3
"""Generate Maharahjong tile rack product reference images using the xAI Grok Imagine API.

Uses GROK_API_KEY from the environment. No third-party dependencies required.

Usage:
    python3 design/racks/generate_rack.py               # generate 3 variants
    python3 design/racks/generate_rack.py --variants 1  # single image
    python3 design/racks/generate_rack.py --dry-run     # print prompt only
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
RACKS_DIR = Path(__file__).parent

RACK_PROMPT = (
    "Premium product photography of a luxury Maharahjong tile rack set, "
    "flat-lay on deep navy/teal neoprene, soft diffused studio lighting with subtle shadows. "
    "Four 19-inch solid wood tile racks in warm honey-walnut stained wood, satin (not glossy) finish, "
    "each accompanied by a matching solid wood pusher of the same finish. "
    "One rack is shown with a row of ivory/cream mahjong tiles standing upright in the groove, "
    "demonstrating how tiles sit in the rack during play. "
    "Small Maharahjong lotus-peacock logo laser-engraved on one end of each rack — "
    "a stylized lotus flower with a peacock feather eye at center, in the manner of an elegant brand mark. "
    "Subtle Devanagari wind direction character engraved on the outer face of each rack: "
    "East/पू, South/द, West/प, North/उ — one per rack, small and elegant. "
    "In one corner of the flat-lay: a deep navy/teal velvet drawstring bag with gold-tone drawstring cord "
    "and brass aglets, small embroidered Maharahjong lotus-peacock logo on the exterior, "
    "sized to hold all four rack-and-pusher pairs. "
    "Warm wood grain visible through the stain. "
    "Overall aesthetic: premium Indian art deco game accessory, warm natural wood tones "
    "against deep navy/teal surface. No text, no watermarks."
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
    parser = argparse.ArgumentParser(description="Generate Maharahjong rack design via xAI API")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling the API")
    parser.add_argument("--variants", type=int, default=3, help="Number of design variants to generate (default: 3)")
    args = parser.parse_args()

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: Set GROK_API_KEY or XAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[DRY RUN] Rack design prompt:\n")
        print(RACK_PROMPT)
        return

    print(f"Generating {args.variants} rack design variant(s)...\n")

    for i in range(1, args.variants + 1):
        out_path = RACKS_DIR / f"rack-design-v{i}.png"
        print(f"  [{i}/{args.variants}] Generating: {out_path.name} ...", end=" ", flush=True)

        try:
            image_bytes = generate_image(RACK_PROMPT, api_key)
            out_path.write_bytes(image_bytes)
            size_kb = len(image_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code})")
            print(f"      {error_body[:200]}")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nDone! Output: {RACKS_DIR}/")


if __name__ == "__main__":
    main()
