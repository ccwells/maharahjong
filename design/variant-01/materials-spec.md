# Maharajong Materials Specification — Variant 01

> **Variant 01: Ivory / Gold / Navy / Ivory** — all four layers opaque acrylic.
> See `design/variant-02/materials-spec.md` for the clear-back alternative.

**Date**: 2026-07-11
**Status**: Confirmed — acrylic for tiles (Chinese OEM); Indian artisan sourcing for wood and brass components
**Informs**: tile blank orders, supplier quotes, component spec updates

## The material language

Three materials, used consistently across every component, with navy and gold
as the connective palette (matching the tile artwork and mat design):

1. **Ivory cast acrylic** — the playing surface (tiles)
2. **Antique brass** — everything metal (dice, trinkets, rack inlay, diya)
3. **Dark rosewood (sheesham)** — everything wooden (racks, pushers)

The coherence is the luxury cue: one metal, one wood, one ivory. Competitor
research (`research/competitor-analysis.md`) shows premium sets ($375–900)
consistently pair layered acrylic tiles with walnut and brass; Maharajong
substitutes sheesham for walnut as a deliberate provenance statement.

## Component decisions

| Component | Material | Key detail |
|-----------|----------|------------|
| Tiles (152) | Four-layer cast acrylic, 32×23×13 mm | Ivory face / gold hairline / lapis-navy core / ivory back — colored edge visible in the wall |
| Racks + pushers (4+4) | Solid sheesham, hand-rubbed oil finish | Single inlaid brass rule line along the top edge |
| Dice (2) | Solid brass, antique patina | Engraved pips filled with navy enamel; rounded corners |
| Scoring trinkets | Solid brass + jewel enamel | Teal peacock-eye, magenta lotus fills (per trinkets spec) |
| Playing mat | Printed micro-suede top, 5 mm dense rubber base | Gold satin-stitch border; same sublimation print as existing mat design |
| Diya light | Solid brass diya, flameless LED insert | Amber flicker LED; real wick cup retained (see `design/diya/diya-design-spec.md`) |

## Why four-layer acrylic for tiles

- **Production-validated**: the only material confirmed against both the
  eufyMake E1 (UV print) and xTool F2 Ultra (laser engraving) in
  `production/tile-production-audit.md`
- **Market-aligned**: layered acrylic is the construction used by The Mahjong
  Line ($375–495) and Oh My Mahjong ($640–900); melamine reads mid-market
- **Visible differentiation**: the navy core + gold hairline shows on every
  tile edge — a from-across-the-room premium cue that echoes the mat border
- **Rejected**: bone/jade (ethics scrutiny per personas research, incompatible
  with UV workflow), melamine (feel), wood-back hybrid (kept as sample only)

## Validation plan (before committing to 100-set MOQ)

1. Order Promlogo sample pack: 4-layer acrylic + melamine + wood-back at
   32×23×13 mm (melamine sample doubles as the "$79 set" marketing reference)
2. Order GUSTARIA Amazon blanks for immediate print/engrave workflow testing
3. Request Jayi prototype sample of the exact 4-layer ivory/gold/navy build
4. Run CMYK test strips + print-then-engrave workflow on all samples
5. Confirm final weight target: 16–19 g per tile (drilled/filled acrylic if
   standard 4-layer comes in light — confirm option with Jayi)

## Supplier outreach

Acrylic tile blanks: `business/outreach/jayi-inquiry-email.md` and
`business/outreach/promlogo-inquiry-email.md`

Indian artisan components: `business/outreach/sheesham-racks-inquiry.md` (racks/pushers)
and `business/outreach/moradabad-brass-inquiry.md` (dice/trinkets).

## Indian artisan sourcing (2026-07-11)

Wood and stone alternatives for tiles were evaluated against the five-constraint tile
spec (UV printable, UV laser engravable, 16–19 g, multi-layer colored edge, 32 × 23 × 13 mm
precision at 152-tile volume) and ruled out:

- **Sheesham**: weight ~8 g/tile (target 16–19 g); cannot produce navy/gold colored edge;
  UV print adhesion requires untested priming workflow; grain variation creates 152-tile QC risk.
- **Makrana marble**: weight ~25.8 g/tile (full set >3.9 kg); material cost 5–15× acrylic;
  brittle under gameplay shuffling; UV print adhesion on polished stone untested.

The three-material language (acrylic / brass / sheesham) is confirmed. Indian artisan
sourcing is directed to the components where it is genuinely superior:

| Component | Indian sourcing cluster |
|-----------|-------------------------|
| Racks + pushers | Jodhpur / Saharanpur / Pravat Timbers (Kolkata) — sheesham with CNC + hand-finish |
| Dice + scoring trinkets | Moradabad — India's brass hub; Jaipur meenakari for enamel fills |
| Diya insert | Moradabad / Jaipur brass workshops |
| Playing mat | Surat — sublimation printing + gold satin-stitch embroidery |

**Post-launch milestone**: Makrana marble collector's edition — limited ultra-premium SKU
(display/heirloom object, not for active gameplay), hand-cut by Jaipur artisans. See
`PROJECT-PLAN.md`.
