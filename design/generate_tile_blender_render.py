#!/usr/bin/env python3
"""
Generate a photorealistic 3D render of the Maharajong blank tile via Blender.

The tile is built as four stacked box meshes (one per material layer), so
proportions are mathematically exact.

Renderer: Cycles (path-traced, Metal GPU on Apple Silicon) with:
  - HDRI studio lighting  (studio_small_08 from Poly Haven)
  - Edge bevels           (0.35mm chamfer, catches specular highlights)
  - Surface imperfections (noise-driven roughness + bump on acrylic faces)
  - Shadow-catching floor plane
  - Subtle camera depth of field

Outputs:
  design/<variant>/manufacturer-docs/tile-blank-3d-render.png

Usage:
    python3 design/generate_tile_blender_render.py --variant variant-01
    python3 design/generate_tile_blender_render.py --variant variant-02
    python3 design/generate_tile_blender_render.py --variant variant-01 --eevee
"""

import sys
from pathlib import Path

BLENDER    = "/Applications/Blender.app/Contents/MacOS/Blender"
DESIGN_DIR = Path(__file__).parent
HDRI_PATH  = DESIGN_DIR / "lib" / "studio_small_08_1k.hdr"
HDRI_URL   = "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr"

# ── Tile constants (mm = Blender units) ────────────────────────────────────────────
W, H, D       = 32, 23, 13      # width (X), face-height (Y), depth (Z)
L1, L2, L3, L4 = 3, 1, 6, 3    # layer thicknesses (Z, top → bottom)
RENDER_W, RENDER_H = 2560, 1600


# =============================================================================
# WRAPPER — called when the script is run directly (bpy not available)
# =============================================================================

def run_as_wrapper() -> None:
    import argparse, subprocess

    parser = argparse.ArgumentParser(
        description="Render the Maharajong tile in 3D via Blender."
    )
    parser.add_argument("--variant", default="variant-01")
    parser.add_argument("--eevee", action="store_true",
                        help="Use EEVEE Next instead of Cycles (faster, less photorealistic)")
    args = parser.parse_args()

    out_dir  = DESIGN_DIR / args.variant / "manufacturer-docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tile-blank-3d-render.png"

    blender_args = [
        BLENDER, "--background",
        "--python", str(Path(__file__).resolve()),
        "--",
        args.variant,
        str(out_path),
        "eevee" if args.eevee else "cycles",
    ]

    engine_name = "EEVEE Next" if args.eevee else "Cycles"
    print(f"Rendering {args.variant} via Blender ({engine_name}) ...",
          end=" ", flush=True)

    result = subprocess.run(blender_args, capture_output=True, text=True,
                            timeout=300)

    if result.returncode != 0:
        print("FAILED")
        # Show only the relevant Blender error lines
        for line in result.stderr.splitlines():
            if any(k in line for k in ("Error", "Traceback", "error", "Python")):
                print(" ", line)
        sys.exit(1)

    kb = out_path.stat().st_size // 1024
    print(f"OK ({kb} KB) → {out_path}")


# =============================================================================
# BLENDER SCENE — called by Blender's Python interpreter (bpy available)
# =============================================================================

def run_as_blender_scene() -> None:
    import bpy
    from mathutils import Vector

    # ── Parse Blender args (after "--") ──────────────────────────────────────────
    sep     = sys.argv.index("--") if "--" in sys.argv else len(sys.argv)
    argv    = sys.argv[sep + 1:]
    variant = argv[0] if len(argv) > 0 else "variant-01"
    output  = argv[1] if len(argv) > 1 else "/tmp/tile_render.png"
    engine  = argv[2] if len(argv) > 2 else "cycles"
    is_v2   = (variant == "variant-02")
    print(f"[blender] variant={variant}  engine={engine}  output={output}")

    # ── Fresh scene ──────────────────────────────────────────────────
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "TileRender"

    # ── sRGB hex → linear float triple ─────────────────────────────────────
    def srgb(h):
        def lin(v):
            c = v / 255.0
            return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
        return (lin(int(h[0:2],16)), lin(int(h[2:4],16)), lin(int(h[4:6],16)))

    # ── Material builder with noise-driven surface imperfections ─────────────
    def make_mat(name, base_rgb, roughness=0.1, metallic=0.0,
                 transmission=0.0, ior=1.45, add_noise=False, add_bump=False):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nodes, links = nt.nodes, nt.links
        nodes.clear()

        out  = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        bsdf.inputs["Base Color"].default_value = (*base_rgb, 1.0)
        bsdf.inputs["Metallic"].default_value   = metallic
        bsdf.inputs["IOR"].default_value        = ior

        for key in ("Transmission Weight", "Transmission"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = transmission
                break
        if transmission > 0:
            mat.blend_method = "HASHED"

        # Shared noise source for roughness + bump
        if add_noise or add_bump:
            coord   = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeMapping")
            noise   = nodes.new("ShaderNodeTexNoise")
            mapping.inputs["Scale"].default_value = (60.0, 60.0, 60.0)
            noise.inputs["Scale"].default_value     = 1.0
            noise.inputs["Detail"].default_value    = 8.0
            noise.inputs["Roughness"].default_value = 0.55
            noise.inputs["Distortion"].default_value = 0.12
            links.new(coord.outputs["Object"],   mapping.inputs["Vector"])
            links.new(mapping.outputs["Vector"],  noise.inputs["Vector"])

        if add_noise:
            # Map noise 0–1 to a narrow roughness band (subtle variation)
            mr = nodes.new("ShaderNodeMapRange")
            mr.inputs["From Min"].default_value = 0.3
            mr.inputs["From Max"].default_value = 0.7
            mr.inputs["To Min"].default_value   = max(0.0, roughness - 0.025)
            mr.inputs["To Max"].default_value   = roughness + 0.035
            links.new(noise.outputs["Fac"], mr.inputs["Value"])
            links.new(mr.outputs["Result"],  bsdf.inputs["Roughness"])
        else:
            bsdf.inputs["Roughness"].default_value = roughness

        if add_bump:
            # Very subtle surface micro-bump (polished acrylic micro-texture)
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value  = 0.04
            bump.inputs["Distance"].default_value  = 0.08
            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

        return mat

    # ── Materials ─────────────────────────────────────────────────────
    m_ivory = make_mat("Ivory_Face", srgb("F5EDD8"),
                       roughness=0.04, add_noise=True, add_bump=True)
    m_gold  = make_mat("Gold",       srgb("D4AF37"),
                       roughness=0.09, metallic=0.94, add_noise=True)
    m_navy  = make_mat("Navy",       srgb("1C2E5E"),
                       roughness=0.07, add_noise=True)
    if is_v2:
        m_back = make_mat("Clear_Back", srgb("1E3060"),
                          roughness=0.02, transmission=0.72, ior=1.49)
    else:
        m_back = make_mat("Ivory_Back", srgb("E8DFC8"),
                          roughness=0.05, add_noise=True, add_bump=True)

    # ── Tile geometry: 4 stacked layers along Z ────────────────────────────
    #  Z-up. Face on top (+Z). Layers: L1 ivory / L2 gold / L3 navy / L4 back.
    layer_defs = [
        (L1, m_ivory, "L1_Ivory_Face"),
        (L2, m_gold,  "L2_Gold"),
        (L3, m_navy,  "L3_Navy"),
        (L4, m_back,  "L4_Back"),
    ]
    tile_objs = []
    cur_z = D / 2.0
    for thickness, mat, name in layer_defs:
        bpy.ops.mesh.primitive_cube_add(size=1.0,
                                        location=(0.0, 0.0, cur_z - thickness / 2.0))
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (float(W), float(H), float(thickness))
        bpy.ops.object.transform_apply(scale=True)
        obj.data.materials.clear()
        obj.data.materials.append(mat)

        # ── Edge bevel: 0.35mm chamfer, angle-limited to outer edges only
        bev = obj.modifiers.new("Bevel", type="BEVEL")
        bev.width        = 0.35      # mm — tight chamfer, just enough to catch light
        bev.segments     = 3         # smooth curve
        bev.profile      = 0.7
        bev.limit_method = "ANGLE"
        bev.angle_limit  = 1.22      # ~70° — only bevel hard exterior corners
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=bev.name)

        tile_objs.append(obj)
        cur_z -= thickness

    # ── Shadow-catching floor plane ──────────────────────────────────────
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -D / 2 - 0.05))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor_mat = bpy.data.materials.new("Floor")
    floor_mat.use_nodes = True
    fn, fl = floor_mat.node_tree.nodes, floor_mat.node_tree.links
    fn.clear()
    fo  = fn.new("ShaderNodeOutputMaterial")
    fd  = fn.new("ShaderNodeBsdfDiffuse")
    fd.inputs["Color"].default_value     = (0.980, 0.980, 0.975, 1.0)
    fd.inputs["Roughness"].default_value = 1.0
    fl.new(fd.outputs["BSDF"], fo.inputs["Surface"])
    floor.data.materials.clear()
    floor.data.materials.append(floor_mat)
    # Cycles shadow catcher: tile shadow on near-white floor
    floor.is_shadow_catcher = True

    # ── Camera ──────────────────────────────────────────────────────────
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens         = 65
    cam_data.sensor_width = 36
    cam_data.dof.use_dof          = True
    cam_data.dof.aperture_fstop   = 11.0   # f/11 — very slight DOF, keeps tile sharp
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector((18.0, -72.0, 44.0))
    target    = Vector((0.0, 0.0, 1.5))
    direction = target - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    # Focus distance = distance from camera to tile centre
    cam_data.dof.focus_distance = (cam_obj.location - Vector((0, 0, 0))).length

    # ── HDRI world lighting ────────────────────────────────────────────
    hdri_path = str(HDRI_PATH)
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    wn, wl = world.node_tree.nodes, world.node_tree.links
    wn.clear()

    w_out  = wn.new("ShaderNodeOutputWorld")
    w_bg   = wn.new("ShaderNodeBackground")
    w_env  = wn.new("ShaderNodeTexEnvironment")
    w_map  = wn.new("ShaderNodeMapping")
    w_tc   = wn.new("ShaderNodeTexCoord")

    try:
        w_env.image = bpy.data.images.load(hdri_path)
        w_bg.inputs["Strength"].default_value = 1.2
        # Rotate HDRI so key light comes from upper-left (matching scene intent)
        w_map.inputs["Rotation"].default_value[2] = 0.9   # ~52°
        wl.new(w_tc.outputs["Generated"], w_map.inputs["Vector"])
        wl.new(w_map.outputs["Vector"],   w_env.inputs["Vector"])
        wl.new(w_env.outputs["Color"],    w_bg.inputs["Color"])
        print("[blender] HDRI loaded")
    except Exception as e:
        # Fallback: plain near-white background
        print(f"[blender] HDRI load failed ({e}), using flat background")
        w_bg.inputs[0].default_value = (0.98, 0.98, 0.975, 1.0)
        w_bg.inputs["Strength"].default_value = 1.0

    wl.new(w_bg.outputs["Background"], w_out.inputs["Surface"])

    # ── Supplemental area lights (boost key + rim over HDRI) ─────────────
    def add_area(name, loc, energy, color=(1,1,1), size=50):
        ld = bpy.data.lights.new(name, type="AREA")
        ld.energy, ld.color, ld.size = energy, color, size
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        scene.collection.objects.link(lo)
        d = Vector((0,0,0)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    add_area("Key",  (-50, -65, 85), energy=8000,
             color=(1.00, 0.97, 0.91), size=55)
    add_area("Rim",  ( 10,  85, -18), energy=4000,
             color=(1.00, 0.95, 0.88), size=40)

    # ── Render settings ────────────────────────────────────────────────
    scene.render.resolution_x          = RENDER_W
    scene.render.resolution_y          = RENDER_H
    scene.render.resolution_percentage = 100
    scene.render.filepath              = output
    scene.render.image_settings.file_format  = "PNG"
    scene.render.image_settings.color_mode  = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent       = False

    if engine == "cycles":
        scene.render.engine          = "CYCLES"
        scene.cycles.samples         = 256
        scene.cycles.use_denoising  = True
        scene.cycles.denoiser        = "OPENIMAGEDENOISE"
        # Enable Metal GPU on Apple Silicon
        try:
            cprefs = bpy.context.preferences.addons["cycles"].preferences
            cprefs.compute_device_type = "METAL"
            cprefs.get_devices()
            for dev in cprefs.devices:
                dev.use = True
            scene.cycles.device = "GPU"
            print("[blender] Cycles Metal GPU enabled")
        except Exception as e:
            print(f"[blender] GPU setup failed ({e}), falling back to CPU")
    else:
        scene.render.engine  = "BLENDER_EEVEE_NEXT"
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 0.3
        try:
            scene.eevee.use_shadows = True
        except Exception:
            pass

    # ── Render ─────────────────────────────────────────────────────────────
    bpy.ops.render.render(write_still=True)


# =============================================================================
# Dispatch
# =============================================================================

try:
    import bpy         # succeeds only when running inside Blender
    run_as_blender_scene()
except ImportError:
    run_as_wrapper()
