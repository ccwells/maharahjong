#!/usr/bin/env python3
"""Generate Maharahjong playing mat design using the xAI Grok Imagine API.

Uses GROK_API_KEY from the environment. No third-party dependencies required.

Usage:
    python3 design/mat/generate_mat.py
    python3 design/mat/generate_mat.py --dry-run
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
MAT_DIR = Path(__file__).parent

MAT_PROMPT = (
    "Top-down overhead view of a premium square mahjong playing mat, "
    "32.5 inches square, deep navy/teal neoprene surface with contrast gold stitching around the edge. "
    "Art style: Indian art deco fusion with gold line art on dark navy background. "
    ""
    "CORNERS: Four corners each feature a gold peacock silhouette facing inward toward center, "
    "with a Devanagari wind direction character beside each peacock — "
    "top-left: North (उ), top-right: East (पू), bottom-left: West (प), bottom-right: South (द). "
    "Each corner has geometric fan/arch framing inspired by Hoysala temple architecture, rendered in gold line art. "
    ""
    "BORDER: Outer edge has a continuous rangoli dot band in gold running the full perimeter. "
    "Inner border is a geometric gold line frame with diamond accent shapes at the midpoint of each side. "
    ""
    "CENTER: A rotated square (diamond) frame in gold contains the Maharahjong logo — "
    "a stylized golden lotus flower with a peacock feather eye emerging from its center. "
    "Surrounding the diamond is a rangoli mandala ring of concentric lotus petals and peacock feather eyes in gold line art. "
    "A larger subtle square outline around the center defines the wall-building play area. "
    ""
    "FIELD: The open playing surface between corners and center is clean deep navy/teal with an extremely subtle "
    "tone-on-tone repeat pattern of tiny rangoli dots, barely visible. "
    ""
    "Overall feel: luxurious, premium, elegant Indian fusion design. Gold on dark navy/teal throughout. "
    "Viewed perfectly flat from directly above as a product photo. No text, no branding text, no watermarks."
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
    parser = argparse.ArgumentParser(description="Generate Maharahjong mat design via xAI API")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling the API")
    parser.add_argument("--variants", type=int, default=3, help="Number of design variants to generate (default: 3)")
    args = parser.parse_args()

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: Set GROK_API_KEY or XAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[DRY RUN] Mat design prompt:\n")
        print(MAT_PROMPT)
        return

    print(f"Generating {args.variants} mat design variant(s)...\n")

    for i in range(1, args.variants + 1):
        out_path = MAT_DIR / f"mat-design-v{i}.png"
        print(f"  [{i}/{args.variants}] Generating: {out_path.name} ...", end=" ", flush=True)

        try:
            image_bytes = generate_image(MAT_PROMPT, api_key)
            out_path.write_bytes(image_bytes)
            size_kb = len(image_bytes) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.readable() else str(e)
            print(f"FAILED ({e.code})")
            print(f"      {error_body[:200]}")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nDone! Output: {MAT_DIR}/")


if __name__ == "__main__":
    main()
