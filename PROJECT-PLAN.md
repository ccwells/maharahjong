# Project Maharahjong Development Plan

## Current Status (Updated 2026-06-08)
- **Active branch**: `design-playing-mat` (PR #20 open)
- **Blocked on**: Shopify domain propagation (maharahjong.com purchased, awaiting DNS)
- **Next up**: Order prototype tile blanks from Amazon; contact Jayi/Promlogo for custom samples; fix tile aspect ratio
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
- [ ] Tile blank material selection — sourcing spec done (`design/tile-blanks-spec.md`), 3 suppliers evaluated
- [ ] Tile mockups, playtesting simulations
- [ ] Digital prototype (medium TBD)

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
- `/design/racks/` — Tile rack design spec
- `/design/dice/` — Dice design spec
- `/design/trinkets/` — Trinkets & accessories design spec
- `/design/marketing/` — Social media teaser images (square, story, landscape)
- `/design/tile-blanks-spec.md` — Tile blank sourcing: 3 suppliers, material comparison, next steps
- `/production/engraving/` — xTool F2 Ultra UV laser engraver spec
- `/production/printing/` — eufyMake E1 UV printer spec
- `/production/tile-production-audit.md` — Compatibility audit: tiles vs. both machines
- `/research/` — Competitor analysis and user research (placeholder)
- `/business/` — Business model and plans (placeholder)
