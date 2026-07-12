# Project Maharajong Development Plan

## Current Status (Updated 2026-07-12)
- **Active branch**: `feat/materials-and-outreach`
- **Blocked on**: Shopify domain propagation (maharajong.com purchased, awaiting DNS)
- **Decided**: Acrylic tiles confirmed; two build variants specified (see `design/variant-01/` and `design/variant-02/`); Indian artisan sourcing for racks/brass/mat
- **Next up**: Order GUSTARIA prototype blanks; send Jayi/Promlogo inquiries (add Variant 02 clear-back note); contact Moradabad/Jodhpur artisans
- **Deferred**: #3, #5, #8 (business/research tasks — on hold until game design is finished)

## Phases & Milestones
### Phase 1: Foundation & Research
- [x] #1 Rules Compilation — `rules/gameplay-rules.md`
- [x] #2 Mood Board Research — `design/moodboard/` (37 images)
- [x] #4 Kanban Setup — [GitHub Project Board](https://github.com/users/ccwells/projects/2)
- [x] #7 Initial Rules Draft — `rules/gameplay-rules.md` v0.1
- [x] #16 Production equipment specs — `production/engraving/` + `production/printing/`
- [x] #11 Playing mat design — `design/mat/mat-design-final.png` (PR #20)
- [ ] #6 Tile Design Concepts — 51 images generated; production audit complete (see `production/tile-production-audit.md`)
- [ ] #12 Tile rack design — spec done (`design/racks/tile-rack-design-spec.md`), needs image
- [ ] #3 Competitor Analysis — deferred
- [ ] #5 User Personas — deferred
- [ ] #8 Business Model Canvas — deferred

### Phase 2: Design & Prototyping
- [ ] #13 Dice design — spec done (`design/dice/dice-design-spec.md`), needs image
- [ ] #14 Trinkets & accessories — spec done (`design/trinkets/trinkets-design-spec.md`), needs image
- [ ] #17 Adapt tile designs for UV printer — audit done, action items: fix aspect ratio (3:4→32:23), CMYK test strips, transparent backgrounds
- [ ] #18 Adapt tile designs for laser engraver — audit done, action items: create SVG engraving overlays, test print-then-engrave workflow
- [ ] #21 Social media teaser image — 3 variants generated (square, story, landscape) in PR #20
- [x] Tile blank material selection — **decided (2026-07-11)**: four-layer acrylic from Jayi/Promlogo; wood/stone alternatives evaluated and ruled out (see `design/variant-01/materials-spec.md`)
- [x] Tile blank design variants — **two variants specified (2026-07-12)**:
  - Variant 01 (MJ-TILE-BLK-001): Ivory / Gold / Navy / Ivory — `design/variant-01/`
  - Variant 02 (MJ-TILE-BLK-002): Ivory / Gold / Navy / Clear — `design/variant-02/`
  - Sample decision: request both variants from Jayi/Promlogo, choose after physical comparison
- [x] Manufacturer spec sheet assets — **generated (2026-07-12)** for both variants:
  - Engineering drawing (SVG + Chromium PNG, exact proportions) — `design/<variant>/manufacturer-docs/tile-blank-technical-drawing.*`
  - Photorealistic renders (Grok 3-view composite) — `design/<variant>/manufacturer-docs/tile-blank-spec-sheet-rendered.png`
  - 3D Blender render (Cycles, HDRI, exact geometry) — `design/<variant>/manufacturer-docs/tile-blank-3d-render.png`
  - Generator scripts: `design/generate_tile_spec_sheet.py`, `design/generate_tile_blender_render.py`
  - Layout reference: `design/TILE-SPEC-SHEET-LAYOUT.md`
- [ ] Source sheesham racks + pushers from Indian artisans — contact Jodhpur/Saharanpur via IndiaMART (`business/outreach/sheesham-racks-inquiry.md`)
- [ ] Source brass dice + scoring trinkets from Moradabad — contact via IndiaMART (`business/outreach/moradabad-brass-inquiry.md`)
- [ ] Source playing mat from Surat sublimation printer with gold satin-stitch embroidery
- [ ] Contact Itz3d Solutions (Chennai) — resin tile marketing batch inquiry (`business/outreach/itz3d-resin-brief.md`)
- [ ] Send Jayi + Promlogo inquiry emails (attach engineering drawings; request both Variant 01 and 02 samples)
- [ ] Order GUSTARIA blanks from Amazon (64 tiles) for immediate UV print/engrave workflow testing
- [ ] Tile mockups, playtesting simulations
- [ ] Digital prototype (medium TBD)
- [ ] **Post-launch**: Makrana marble collector's edition — limited ultra-premium SKU, hand-cut by Jaipur artisans, priced $2,000–$5,000+ (display/heirloom, not active gameplay)

### Phase 3: Ecommerce Setup
- [ ] #22 Shopify store setup & domain — account created, domain purchased, awaiting DNS propagation
- [ ] #23 Storefront theme design & brand customization
- [ ] #24 Product catalog & listings
- [ ] #25 Payment processing & checkout optimization
- [ ] #26 Shipping, fulfillment & packaging
- [ ] #27 Legal compliance, policies & data protection
- [ ] #28 SEO optimization & search visibility
- [ ] #29 Analytics, tracking & conversion measurement
- [ ] #30 Email marketing & automation flows
- [ ] #31 Pre-launch QA & testing
- [ ] #32 Launch marketing plan & go-live

## Repository Structure
- `README.md` — Vision + generation script usage
- `AGENTS.md` — Agent instructions (Grok for images)
- `rules/gameplay-rules.md` — Complete rules v0.1
- `/design/moodboard/` — 37 moodboard images (rangoli, temples, peacock, spice)
- `/design/tiles/` — 51 tile images, `generate_tiles.py`, `tile-design-spec.md`
- `/design/mat/` — Mat design final + spec + `generate_mat.py`
- `/design/racks/` — Tile rack design spec (Indian artisan sourcing notes)
- `/design/dice/` — Dice design spec
- `/design/trinkets/` — Trinkets & accessories design spec
- `/design/marketing/` — Social media teaser images (square, story, landscape)
- `/design/variant-01/` — Tile blank Variant 01: Ivory/Gold/Navy/Ivory (confirmed spec)
  - `materials-spec.md`, `tile-blanks-spec.md`, `manufacturer-docs/`
- `/design/variant-02/` — Tile blank Variant 02: Ivory/Gold/Navy/Clear (design proposal)
  - `materials-spec.md`, `tile-blanks-spec.md`, `manufacturer-docs/`
- `/design/generate_tile_spec_sheet.py` — Generates SVG engineering drawing + Grok render for any variant
- `/design/generate_tile_blender_render.py` — Generates photorealistic 3D render via Blender Cycles
- `/design/TILE-SPEC-SHEET-LAYOUT.md` — SVG layout reference + variant creation guide
- `/design/lib/` — Three.js r152 + Poly Haven studio HDRI (required by generators)
- `/production/engraving/` — xTool F2 Ultra UV laser engraver spec
- `/production/printing/` — eufyMake E1 UV printer spec
- `/production/tile-production-audit.md` — Compatibility audit: tiles vs. both machines
- `/business/outreach/` — Supplier inquiry email drafts (Jayi, Promlogo, Itz3d, Moradabad, Jodhpur)
- `/research/` — Competitor analysis and user research (placeholder)
