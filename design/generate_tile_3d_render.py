#!/usr/bin/env python3
"""
Generate a photorealistic 3D render of the Maharajong blank tile using
a Three.js scene rendered via Playwright/Chromium.

The tile is built as four stacked BoxGeometry meshes — one per layer —
so layer proportions are mathematically exact, not AI-approximated.

Outputs:
  design/<variant>/manufacturer-docs/tile-blank-3d-render.png

Usage:
    python3 design/generate_tile_3d_render.py --variant variant-01
    python3 design/generate_tile_3d_render.py --variant variant-02
"""

import argparse
import http.server
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
DESIGN_DIR = Path(__file__).parent
LIB_DIR    = DESIGN_DIR / "lib"
THREE_JS   = LIB_DIR / "three.min.js"
THREE_URL  = "https://unpkg.com/three@0.152.2/build/three.min.js"

# ── Tile constants (mm = scene units) ────────────────────────────────────────
W  = 32   # tile width  (X)
TH = 23   # tile face height (Z — the tile lies face-up, Z is its length)
D  = 13   # tile depth  (Y — layers run along Y, face on top)
L1 = 3    # Layer 1: ivory face   (top)
L2 = 1    # Layer 2: gold hairline
L3 = 6    # Layer 3: lapis navy core
L4 = 3    # Layer 4: back (ivory V01 / crystal-clear V02)

RENDER_W = 2560
RENDER_H = 1600


# ── Three.js download ────────────────────────────────────────────────────────

def ensure_threejs() -> None:
    LIB_DIR.mkdir(exist_ok=True)
    if THREE_JS.exists():
        return
    print(f"Downloading Three.js r152 → {THREE_JS.relative_to(DESIGN_DIR)} ...",
          end=" ", flush=True)
    urllib.request.urlretrieve(THREE_URL, THREE_JS)
    print(f"OK ({THREE_JS.stat().st_size // 1024} KB)")


# ── HTML scene template ──────────────────────────────────────────────────────
# Written as a plain string (no f-string) to avoid curly-brace escaping hell.
# Two placeholders are substituted: BACK_MAT_CODE and VARIANT_LABEL.

SCENE_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; padding: 0; background: #FAFAF8; overflow: hidden; }
  canvas { display: block; }
</style>
</head>
<body>
<script src="/lib/three.min.js"></script>
<script>
// ─── Tile spec (1 unit = 1 mm) ─────────────────────────────────────────────
const TW = TILE_W;    // width  (X)
const TH = TILE_TH;  // face height (Z, tile lies face-up)
const TD = TILE_D;   // depth  (Y, layers run along Y)
const l1 = LAYER_1, l2 = LAYER_2, l3 = LAYER_3, l4 = LAYER_4;

// ─── Renderer ──────────────────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(REND_W, REND_H);
renderer.setPixelRatio(1);
renderer.toneMapping    = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled   = true;
renderer.shadowMap.type      = THREE.PCFSoftShadowMap;
renderer.outputColorSpace    = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

// ─── Scene & camera ────────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xFAFAF8);

// Narrow FOV (30°) gives the clean compression of product photography.
const camera = new THREE.PerspectiveCamera(30, REND_W / REND_H, 0.1, 2000);
// Slightly in front and elevated, centred on the long axis.
// This shows: face (top), front long edge (all 4 layers), a bit of right edge.
camera.position.set(10, 32, 62);
camera.lookAt(0, -1, 0);

// ─── Materials ─────────────────────────────────────────────────────────────
const matIvory = new THREE.MeshStandardMaterial({
    color: 0xF5EDD8, roughness: 0.05, metalness: 0.0,
    envMapIntensity: 0.9
});
const matGold = new THREE.MeshStandardMaterial({
    color: 0xD4AF37, roughness: 0.10, metalness: 0.92,
    envMapIntensity: 1.6
});
const matNavy = new THREE.MeshStandardMaterial({
    color: 0x1C2E5E, roughness: 0.07, metalness: 0.06,
    envMapIntensity: 0.5
});
const matBack = BACK_MAT_CODE;

// ─── Tile geometry — 4 stacked BoxGeometry layers along Y axis ─────────────
//
//   Y = +TD/2  ←── top: ivory face (L1)
//              ←── gold hairline   (L2)
//              ←── lapis navy core (L3)  ← widest band
//   Y = -TD/2  ←── bottom: back   (L4)
//
// The tile face (XZ plane) faces upward (+Y). Camera looks slightly down.

const tileGroup = new THREE.Group();

const layerDefs = [
    { mat: matIvory, depth: l1 },   // top — ivory face
    { mat: matGold,  depth: l2 },   // gold hairline
    { mat: matNavy,  depth: l3 },   // navy core
    { mat: matBack,  depth: l4 },   // bottom — back
];

let topY = TD / 2;
for (const def of layerDefs) {
    const geo  = new THREE.BoxGeometry(TW, def.depth, TH);
    const mesh = new THREE.Mesh(geo, def.mat);
    mesh.position.y = topY - def.depth / 2;
    mesh.castShadow    = true;
    mesh.receiveShadow = true;
    tileGroup.add(mesh);
    topY -= def.depth;
}

// Very slight rotation on Y axis to reveal depth and add visual interest.
tileGroup.rotation.y = 0.18;  // ~10°
scene.add(tileGroup);

// ─── Subtle ground shadow plane ─────────────────────────────────────────────
const groundMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(500, 500),
    new THREE.ShadowMaterial({ opacity: 0.10 })
);
groundMesh.rotation.x = -Math.PI / 2;
groundMesh.position.y  = -TD / 2 - 0.05;
groundMesh.receiveShadow = true;
scene.add(groundMesh);

// ─── Lighting ───────────────────────────────────────────────────────────────
// Ambient — soft base fill
scene.add(new THREE.AmbientLight(0xfff8f0, 0.40));

// Key light — main studio light, upper-left-front, warm white
const key = new THREE.DirectionalLight(0xfffaf0, 3.8);
key.position.set(-55, 110, 70);
key.castShadow = true;
key.shadow.mapSize.width  = 2048;
key.shadow.mapSize.height = 2048;
key.shadow.camera.near  =   1;
key.shadow.camera.far   = 300;
key.shadow.camera.left  = -70;
key.shadow.camera.right =  70;
key.shadow.camera.top   =  50;
key.shadow.camera.bottom = -50;
key.shadow.bias = -0.0004;
scene.add(key);

// Fill light — right side, cool-ish white, soft
const fill = new THREE.DirectionalLight(0xe0eeff, 0.9);
fill.position.set(80, 30, 40);
scene.add(fill);

// Back/rim light — from behind, slightly warm, lifts tile from background
const rim = new THREE.DirectionalLight(0xffeecc, 0.55);
rim.position.set(5, -20, -90);
scene.add(rim);

// Top light — rakes lightly across the face surface
const topLight = new THREE.DirectionalLight(0xffffff, 0.30);
topLight.position.set(0, 150, 10);
scene.add(topLight);

// ─── Render ─────────────────────────────────────────────────────────────────
renderer.render(scene, camera);
window._renderDone = true;
</script>
</body>
</html>
"""


def build_html(variant: str) -> str:
    is_v2 = (variant == "variant-02")

    if is_v2:
        # Crystal-clear acrylic back — navy core visible through it.
        # MeshPhysicalMaterial with transmission approximates this.
        back_mat = (
            "new THREE.MeshPhysicalMaterial({"
            "  color: 0x2A4070,"      # navy tinted (seen through 3mm clear)
            "  roughness: 0.02,"
            "  metalness: 0.0,"
            "  transmission: 0.70,"  # let light pass through
            "  thickness: 3.0,"
            "  transparent: true,"
            "  ior: 1.49,"           # acrylic IOR
            "  clearcoat: 1.0,"
            "  clearcoatRoughness: 0.01"
            "})"
        )
    else:
        back_mat = (
            "new THREE.MeshStandardMaterial({"
            "  color: 0xE8DFC8,"
            "  roughness: 0.06,"
            "  metalness: 0.0"
            "})"
        )

    html = (SCENE_TEMPLATE
            .replace("BACK_MAT_CODE",  back_mat)
            .replace("TILE_W",  str(W))
            .replace("TILE_TH", str(TH))
            .replace("TILE_D",  str(D))
            .replace("LAYER_1", str(L1))
            .replace("LAYER_2", str(L2))
            .replace("LAYER_3", str(L3))
            .replace("LAYER_4", str(L4))
            .replace("REND_W",  str(RENDER_W))
            .replace("REND_H",  str(RENDER_H)))
    return html


# ── Local HTTP server ─────────────────────────────────────────────────────────

class _SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass  # suppress request logs


def start_server(directory: Path) -> tuple[http.server.HTTPServer, int]:
    import socket
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = http.server.HTTPServer(
        ("127.0.0.1", port),
        lambda *a, **k: _SilentHTTPHandler(*a, directory=str(directory), **k),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


# ── Playwright capture (subprocess to python3.11 if needed) ──────────────────

_CAPTURE_SCRIPT = """\
import sys
from playwright.sync_api import sync_playwright
url, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": w, "height": h})
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    # Wait until Three.js signals rendering is complete
    page.wait_for_function("window._renderDone === true", timeout=20000)
    page.wait_for_timeout(200)
    page.screenshot(path=out,
                    clip={"x": 0, "y": 0, "width": w, "height": h},
                    timeout=30000)
    browser.close()
"""


def capture(url: str, out_path: Path) -> None:
    # Try current interpreter first
    try:
        from playwright.sync_api import sync_playwright   # noqa: F401
        _capture_inline(url, out_path)
        return
    except ImportError:
        pass

    # Fall back to a Python that has playwright
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(_CAPTURE_SCRIPT)
        script = f.name

    try:
        for py in ["python3.11", "python3.10", "python3.13"]:
            try:
                chk = subprocess.run([py, "-c", "import playwright"],
                                     capture_output=True)
                if chk.returncode != 0:
                    continue
                res = subprocess.run(
                    [py, script, url, str(out_path),
                     str(RENDER_W), str(RENDER_H)],
                    capture_output=True, text=True, timeout=60,
                )
                if res.returncode != 0:
                    raise RuntimeError(res.stderr[-600:])
                return
            except FileNotFoundError:
                continue
        raise RuntimeError(
            "playwright not found. Run: "
            "python3.11 -m pip install playwright && "
            "python3.11 -m playwright install chromium"
        )
    finally:
        Path(script).unlink(missing_ok=True)


def _capture_inline(url: str, out_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": RENDER_W, "height": RENDER_H})
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_function("window._renderDone === true", timeout=20000)
        page.wait_for_timeout(200)
        page.screenshot(path=str(out_path),
                        clip={"x": 0, "y": 0,
                              "width": RENDER_W, "height": RENDER_H},
                        timeout=30000)
        browser.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a 3D product image of the Maharajong blank tile "
                    "using Three.js geometry (exact proportions)."
    )
    parser.add_argument("--variant", default="variant-01",
                        help="Tile variant (default: variant-01)")
    args = parser.parse_args()

    # Ensure Three.js is available locally
    ensure_threejs()

    # Write the scene HTML into the design dir (served by local HTTP server)
    html_path = DESIGN_DIR / "_tile_3d_scene.html"
    html_path.write_text(build_html(args.variant), encoding="utf-8")

    out_dir = DESIGN_DIR / args.variant / "manufacturer-docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tile-blank-3d-render.png"

    # Start local HTTP server rooted at design/ so /lib/three.min.js resolves
    server, port = start_server(DESIGN_DIR)
    url = f"http://127.0.0.1:{port}/_tile_3d_scene.html"

    try:
        print(f"Rendering {args.variant} via Three.js + Chromium ...",
              end=" ", flush=True)
        capture(url, out_path)
        print(f"OK ({out_path.stat().st_size // 1024} KB) → {out_path}")
    finally:
        server.shutdown()
        html_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
