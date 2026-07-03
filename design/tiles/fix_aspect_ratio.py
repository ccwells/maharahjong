#!/usr/bin/env python3
"""Crop Maharajong tile images to the exact physical tile-face aspect ratio.

The physical tile face is 32 x 23 mm. Tiles are generated in portrait
orientation, so the exact target image proportion is 23:32 (width:height =
0.71875). The Grok Imagine API returns the closest standard ratio it supports
(most tiles come back at 3:4 = 0.750, some at ~1712x2432 = 0.704), which is
~4% off the tile face. This tool center-crops each PNG to the exact tile-face
proportion, preserving the original orientation, and writes the result to a
separate ``print-ready/`` directory so the originals are kept as reference
(per the production audit).

Backends are auto-detected, so no install is required on macOS:
  * Pillow (PIL) if importable -- portable, preferred.
  * macOS ``sips`` as a fallback.

Usage:
    python3 design/tiles/fix_aspect_ratio.py            # crop all tiles -> print-ready/
    python3 design/tiles/fix_aspect_ratio.py --dry-run  # show planned crops only
    python3 design/tiles/fix_aspect_ratio.py --out /tmp/pr  # custom output dir
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Physical tile face (mm). Long side : short side = 32 : 23.
TILE_LONG_MM = 32
TILE_SHORT_MM = 23

TILES_DIR = Path(__file__).parent
DEFAULT_OUT = TILES_DIR / "print-ready"

# Source categories (mirror generate_tiles.py output layout).
CATEGORIES = [
    "suit-lotus",
    "suit-peacock",
    "suit-vedic",
    "honors",
    "bonus-festival",
    "bonus-chakra",
    "tile-back",
]


def target_dims(w: int, h: int) -> tuple[int, int]:
    """Centered-crop (width, height) matching the 32:23 tile-face proportion.

    The image's current orientation is preserved: for a portrait image the long
    side is the height (height:width = 32:23); for landscape it is the width.
    """
    if h >= w:  # portrait -> long side is height
        target_wh = TILE_SHORT_MM / TILE_LONG_MM  # 23/32 = 0.71875
    else:  # landscape -> long side is width
        target_wh = TILE_LONG_MM / TILE_SHORT_MM  # 32/23

    cur = w / h
    if cur > target_wh:  # too wide -> trim width
        return max(1, round(h * target_wh)), h
    if cur < target_wh:  # too tall -> trim height
        return w, max(1, round(w / target_wh))
    return w, h  # already exact


def detect_backend() -> str:
    """Return 'pillow', 'sips', or '' (none available)."""
    try:
        import PIL  # noqa: F401

        return "pillow"
    except Exception:
        pass
    if shutil.which("sips") is not None:
        return "sips"
    return ""


def read_size(path: Path, backend: str) -> tuple[int, int]:
    if backend == "pillow":
        from PIL import Image

        with Image.open(path) as im:
            return im.width, im.height

    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    w = h = 0
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            w = int(line.split(":")[1])
        elif line.startswith("pixelHeight:"):
            h = int(line.split(":")[1])
    if not (w and h):
        raise RuntimeError(f"could not read dimensions for {path}")
    return w, h


def crop_centered(src: Path, dst: Path, tw: int, th: int, backend: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if backend == "pillow":
        from PIL import Image

        with Image.open(src) as im:
            left = (im.width - tw) // 2
            top = (im.height - th) // 2
            im.crop((left, top, left + tw, top + th)).save(dst)
        return

    # sips -c crops centered to <height> <width>.
    subprocess.run(
        ["sips", "-c", str(th), str(tw), str(src), "--out", str(dst)],
        capture_output=True,
        text=True,
        check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Center-crop tiles to the exact 32:23 tile-face aspect ratio"
    )
    ap.add_argument("--src", type=Path, default=TILES_DIR, help="source tiles dir")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output dir")
    ap.add_argument("--dry-run", action="store_true", help="print planned crops only")
    args = ap.parse_args()

    backend = detect_backend()
    if not backend:
        print(
            "ERROR: no image backend. Install Pillow (pip install Pillow) "
            "or run on macOS (sips).",
            file=sys.stderr,
        )
        return 1

    target_wh = TILE_SHORT_MM / TILE_LONG_MM
    print(
        f"Backend: {backend} | target portrait W:H = "
        f"{TILE_SHORT_MM}:{TILE_LONG_MM} = {target_wh:.5f}\n"
    )

    pngs: list[Path] = []
    out_resolved = args.out.resolve()
    for cat in CATEGORIES:
        d = args.src / cat
        if d.is_dir():
            for png in sorted(d.glob("*.png")):
                # Don't reprocess our own output if it lives under src.
                if out_resolved in png.resolve().parents:
                    continue
                pngs.append(png)
    if not pngs:
        print("No tile PNGs found.")
        return 1

    cropped = exact = 0
    for src in pngs:
        w, h = read_size(src, backend)
        tw, th = target_dims(w, h)
        rel = src.relative_to(args.src)
        dst = args.out / rel
        if (tw, th) == (w, h):
            print(f"  {rel}: exact ({w}x{h})")
            exact += 1
        else:
            print(f"  {rel}: {w}x{h} -> {tw}x{th}")
            cropped += 1
        if not args.dry_run:
            crop_centered(src, dst, tw, th, backend)

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(
        f"\n{prefix}Processed {len(pngs)} tiles "
        f"({cropped} cropped, {exact} already exact)."
    )
    if not args.dry_run:
        print(f"Output: {args.out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
