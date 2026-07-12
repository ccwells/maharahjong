# Maharajong Tile Blanks Sourcing Spec — Variant 02

> **Variant 02: Ivory / Gold / Navy / Clear** — crystal-clear acrylic back face;
> navy core visible through the back. See `design/variant-01/tile-blanks-spec.md`
> for the all-opaque original.

> **Material decision (2026-07-12)**: Four-layer cast acrylic — ivory face /
> gold hairline / lapis-navy core / **crystal-clear back** — design proposal,
> pending physical sample comparison against Variant 01.
> Full rationale: `design/variant-02/materials-spec.md`.
> Supplier inquiries: `business/outreach/jayi-inquiry-email.md` (add clear-back
> note) and `business/outreach/promlogo-inquiry-email.md` (add clear-back note).

## Target Tile Dimensions

Same as Variant 01 — no change.

- **Size**: 32 × 23 × 13 mm
- **Quantity per set**: 152 tiles
- **Surface**: Smooth, polished — face must accept UV printing and UV laser engraving
- **Face color**: Ivory/cream (Layer 1)
- **Back appearance**: Deep navy (Layer 3 seen through crystal-clear Layer 4)

## Layer Stack

```
FACE (UV print surface)
┌─────────────────────────────────┐
│ L1  Ivory/cream acrylic   3 mm  │  Pantone ~9183 C  — UV print here
│─────────────────────────────────│
│ L2  Metallic gold         1 mm  │  Pantone ~874 C   — edge hairline
│─────────────────────────────────│
│ L3  Lapis navy            6 mm  │  Pantone ~289 C   — core / visible through back
│─────────────────────────────────│
│ L4  Crystal-clear acrylic 3 mm  │  Water-white, zero haze — back face
└─────────────────────────────────┘
BACK (navy visible through clear)
```

**Key difference from Variant 01**: Layer 4 is optically clear instead of ivory.
The navy core (Layer 3) shows through the clear back face — the back of the tile
appears deep navy without any printing.

---

## Supplier 1: Jayi Acrylic (OEM/ODM — recommended for production)

Same capabilities as documented in `design/variant-01/tile-blanks-spec.md`.

### Variant 02 amendment for Jayi inquiry

Add the following to the Jayi inquiry email (`business/outreach/jayi-inquiry-email.md`):

> **Additional sample request (Variant 02)**: In addition to the ivory-back
> sample, please also quote a version where Layer 4 (back face, 3mm) is
> **crystal-clear cast acrylic** instead of ivory — optically clear, water-white,
> zero haze or frosting. We want to compare the ivory-back and clear-back builds
> side-by-side. Please confirm:
> - Is crystal-clear PMMA available as a standard layer option?
> - Will the polishing process leave the clear layer optically clear (no
>   accidental frosting from buffing compounds)?
> - Is there any price difference vs. the ivory-back build?

### Maharajong fit (Variant 02)

- ✅ Crystal-clear PMMA is standard stock for all acrylic manufacturers
- ✅ No Pantone matching needed for Layer 4 — simpler than matched ivory
- ✅ Navy core visibility through clear back confirmed (physics — no additional
  process needed)
- ⚠️ **New QC requirement**: back-face clarity must be inspected per tile —
  no milky patches, no interface delamination at Layer 3/4 boundary
- ⚠️ Polishing process must not frost the clear back — confirm with Jayi that
  buffing compounds used on ivory are not applied to the clear layer

---

## Supplier 2: Promlogo (blank tile supplier)

Same capabilities as Variant 01. When requesting samples, add:

> **Variant 02 sample**: Please include one additional sample batch of 20 tiles
> in the 4-layer acrylic build where the back layer is **crystal-clear** (not
> ivory/cream). We want to see the navy core visible through the clear back.
> If you do not offer clear-back as a standard option, please let us know.

### Maharajong fit (Variant 02)

- ✅ Promlogo lists "jelly / candy / transparent" layer options — clear back
  likely available as a standard configuration
- ✅ Blank surface on face for UV printing unchanged
- ⚠️ Request confirmation that their clear layer is optically water-white
  (some transparent acrylics have a slight blue or green tint)

---

## Supplier 3: GUSTARIA via Amazon (prototyping only)

White plastic tiles — not applicable for Variant 02 testing. The clear-back effect
requires a genuine multi-layer acrylic construction; the GUSTARIA single-layer plastic
tile cannot replicate it. Use Jayi/Promlogo samples only for Variant 02 evaluation.

---

## Material Comparison: Variant 01 vs. Variant 02

| Property | Variant 01 (Ivory back) | Variant 02 (Clear back) |
|----------|------------------------|------------------------|
| Back face appearance | Ivory/cream | Deep navy (through clear) |
| Table field during play | Ivory field when tiles face-down | Navy field when tiles face-down |
| Edge profile | Ivory / Gold / Navy / Ivory | Ivory / Gold / Navy / Clear(→Navy) |
| Layer 4 sourcing | Pantone-matched ivory PMMA | Standard water-white clear PMMA |
| Layer 4 QC | Color match to Layer 1 | Optical clarity (no haze) |
| UV printing | Face only | Face only (back intentionally clear) |
| Weight | 16–19 g (same) | 16–19 g (same — clear PMMA = same density) |
| Manufacturer complexity | Standard | Marginally simpler (no ivory match for L4) |
| Visual differentiation | Strong (ivory face, colored edge) | Stronger (navy back adds second distinct face) |
| Market precedent | Standard premium acrylic mahjong | No known competitor offers this |

### Recommendation

Request **both variants** in the Jayi and Promlogo sample packs. The clear-back
variant is a potentially stronger differentiator at negligible added manufacturing
complexity, but the real-world visual needs physical validation — does the navy
core read clearly, or is the clear acrylic layer too thick/tinted to produce a
saturated navy back? Samples will answer this question definitively.

---

## Next Steps

1. **Add Variant 02 note** to Jayi and Promlogo inquiry emails before sending
2. **Request dual samples** — both ivory-back (Variant 01) and clear-back (Variant 02)
   in a single sample order from each supplier
3. **Compare on the table**: Place both variants face-down in a simulated wall; evaluate
   the navy-back effect at table distance (~60 cm) in normal room lighting
4. **Decide variant** before committing to production MOQ
5. **Update PROJECT-PLAN.md** once variant is chosen
