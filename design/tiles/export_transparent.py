#!/usr/bin/env python3
"""Export transparent-background versions of all print-ready tile images for UV printing.

Background context
------------------
The Grok-generated tiles have an ivory/cream background.  When UV-printing onto
pre-coloured tile blanks the background should NOT be printed — only the artwork
and gold border.  This script replaces the background with alpha transparency
and writes the results to ``transparent/``, leaving the ``print-ready/``
originals untouched.

Algorithm: dual-constraint BFS flood-fill
------------------------------------------
Seeds are taken from all four edges of the image, restricted to pixels whose
average brightness is above a threshold (≥150/255) so that dark design
elements that happen to touch the image border are skipped.

The background colour is estimated as the median of all seed pixels collected
from the borders.  The BFS then applies two simultaneous constraints:

  1. Relative constraint (rel_tolerance, default 30): each candidate pixel must
     be within this Euclidean RGB distance of the pixel that *discovered* it.
     This lets the fill follow gentle brightness gradients within the background.

  2. Absolute constraint (abs_tolerance, default 70): each candidate pixel must
     be within this Euclidean RGB distance of the estimated background colour.
     This anchors the fill to the ivory/cream colour family and prevents it
     from drifting step-by-step into richly coloured design areas — even when
     each individual step would appear small (e.g. the iridescent gradient in
     the Peacock suit or chakra wild tiles).

Both constraints must be satisfied; the absolute constraint is the safety
guard against runaway drift.  Empirically validated on all 51 tiles.

Requirements
------------
Pillow (PIL) is required — sips does not support alpha channel operations.

    pip install Pillow          # if not already installed

Usage
-----
    python3.10 design/tiles/export_transparent.py                  # all 51 tiles
    python3.10 design/tiles/export_transparent.py --dry-run        # count only
    python3.10 design/tiles/export_transparent.py --tolerance 45   # looser fill
    python3.10 design/tiles/export_transparent.py --src path/to/print-ready
    python3.10 design/tiles/export_transparent.py --out path/to/custom-out
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

TILES_DIR = Path(__file__).parent
DEFAULT_SRC = TILES_DIR / "print-ready"
DEFAULT_OUT = TILES_DIR / "transparent"

# Brightness below which a border pixel is treated as a design element,
# not background — skipped as a seed.
BORDER_BRIGHTNESS_MIN = 150


def _require_pillow() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print(
            "ERROR: Pillow is required for transparency export.\n"
            "  Install: pip install Pillow  (or pip3.10 install Pillow)\n"
            "  sips cannot produce transparent PNGs.",
            file=sys.stderr,
        )
        sys.exit(1)


def remove_background(
    src: Path,
    rel_tolerance: int = 30,
    abs_tolerance: int = 70,
) -> "Image":  # type: ignore[name-defined]
    """Return a copy of the image with the background made transparent.

    Parameters
    ----------
    src:            Path to the source PNG (no alpha required).
    rel_tolerance:  Max Euclidean RGB distance from a candidate pixel to its
                    flood-fill parent (default 30).  Controls gradient tracking.
    abs_tolerance:  Max Euclidean RGB distance from a candidate pixel to the
                    estimated background colour (default 70).  Prevents runaway
                    drift into richly coloured design areas.
    """
    import math

    import numpy as np
    from PIL import Image

    img = Image.open(src).convert("RGBA")
    data = np.array(img, dtype=np.int32)
    h, w = data.shape[:2]

    visited = np.zeros((h, w), dtype=bool)
    mask = np.zeros((h, w), dtype=bool)
    seed_colors: list[tuple[int, int, int]] = []

    queue: deque[tuple[int, int]] = deque()

    def _seed(y: int, x: int) -> None:
        if visited[y, x]:
            return
        r, g, b = int(data[y, x, 0]), int(data[y, x, 1]), int(data[y, x, 2])
        if (r + g + b) // 3 >= BORDER_BRIGHTNESS_MIN:
            visited[y, x] = True
            queue.append((y, x))
            seed_colors.append((r, g, b))

    # Seed from all four border rows/columns.
    for x in range(w):
        _seed(0, x)
        _seed(h - 1, x)
    for y in range(h):
        _seed(y, 0)
        _seed(y, w - 1)

    # Estimate background colour as median of seeded border pixels.
    bg = (
        tuple(int(v) for v in map(lambda c: sorted(c)[len(c) // 2], zip(*seed_colors)))
        if seed_colors
        else (240, 235, 215)
    )
    bg_r, bg_g, bg_b = bg

    # Dual-constraint BFS.
    neighbours = ((-1, 0), (1, 0), (0, -1), (0, 1))
    while queue:
        y, x = queue.popleft()
        mask[y, x] = True
        py_r, py_g, py_b = int(data[y, x, 0]), int(data[y, x, 1]), int(data[y, x, 2])

        for dy, dx in neighbours:
            ny, nx = y + dy, x + dx
            if ny < 0 or ny >= h or nx < 0 or nx >= w:
                continue
            if visited[ny, nx]:
                continue
            nr, ng, nb = int(data[ny, nx, 0]), int(data[ny, nx, 1]), int(data[ny, nx, 2])
            # Relative: must be close to the discovering pixel.
            rel_dist = math.sqrt((nr - py_r) ** 2 + (ng - py_g) ** 2 + (nb - py_b) ** 2)
            if rel_dist > rel_tolerance:
                continue
            # Absolute: must stay within the background colour family.
            abs_dist = math.sqrt((nr - bg_r) ** 2 + (ng - bg_g) ** 2 + (nb - bg_b) ** 2)
            if abs_dist > abs_tolerance:
                continue
            visited[ny, nx] = True
            queue.append((ny, nx))

    # Apply: background pixels → fully transparent.
    result = np.array(img)
    result[mask, 3] = 0
    return Image.fromarray(result, "RGBA")


def collect_tiles(src_dir: Path) -> list[Path]:
    """Return all PNG files under src_dir, sorted."""
    return sorted(src_dir.rglob("*.png"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export transparent-background tile PNGs for UV printing"
    )
    ap.add_argument(
        "--src",
        type=Path,
        default=DEFAULT_SRC,
        metavar="DIR",
        help=f"source directory of print-ready tiles (default: {DEFAULT_SRC})",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        metavar="DIR",
        help=f"output directory for transparent tiles (default: {DEFAULT_OUT})",
    )
    ap.add_argument(
        "--rel-tolerance",
        type=int,
        default=30,
        metavar="N",
        dest="rel_tolerance",
        help=(
            "Max RGB distance from a pixel to its flood-fill parent (default: 30). "
            "Increase if background patches remain; decrease if colours bleed."
        ),
    )
    ap.add_argument(
        "--abs-tolerance",
        type=int,
        default=70,
        metavar="N",
        dest="abs_tolerance",
        help=(
            "Max RGB distance from a pixel to the estimated background colour (default: 70). "
            "Safety guard preventing drift into richly coloured design areas."
        ),
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="list tiles that would be processed, then exit",
    )
    args = ap.parse_args()

    if not args.dry_run:
        _require_pillow()

    pngs = collect_tiles(args.src)
    if not pngs:
        print(f"No PNG files found under {args.src}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"[DRY RUN] Would process {len(pngs)} tile(s) from {args.src}")
        for p in pngs:
            rel = p.relative_to(args.src)
            print(f"  {rel}")
        print(f"\nOutput directory: {args.out}")
        print(f"rel-tolerance={args.rel_tolerance}  abs-tolerance={args.abs_tolerance}")
        return 0

    print(
        f"Exporting {len(pngs)} transparent tile(s) "
        f"(rel-tol={args.rel_tolerance}, abs-tol={args.abs_tolerance})...\n"
    )

    ok = failed = 0
    for src in pngs:
        rel = src.relative_to(args.src)
        dst = args.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        print(f"  {rel} ...", end=" ", flush=True)
        try:
            result = remove_background(
                src,
                rel_tolerance=args.rel_tolerance,
                abs_tolerance=args.abs_tolerance,
            )
            result.save(dst, "PNG")
            size_kb = dst.stat().st_size // 1024
            print(f"OK ({size_kb} KB)")
            ok += 1
        except Exception as exc:
            print(f"FAILED: {exc}")
            failed += 1

    print(f"\nDone: {ok} exported, {failed} failed.")
    print(f"Output: {args.out}/")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
