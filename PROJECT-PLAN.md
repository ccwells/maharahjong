# Project Maharajong Development Plan

## Current Status (Updated 2026-07-03)
- **Live**: Pre-order landing page is the homepage at [maharajong.com](https://maharajong.com) — waitlist email capture working (customers tagged `preorder`), password protection removed
- **Store**: Shopify Advanced; draft "Founding Edition" product created ($399 placeholder, SKU MRJ-FE-001); homepage SEO title/description set; main nav menu rebuilt
- **Research**: Competitor analysis, user personas, and business model canvas complete (see `research/` and `business/`) — headline: no direct Indian-fusion competitor exists; viable price corridor $329–$399 (+$499 Founding tier)
- **Next up (critical path)**: decide tile blank material → order prototype blanks (Amazon) + custom samples (Jayi/Promlogo) → CMYK test strips → print-then-engrave workflow tests
- **Open items**: social sharing image in Online Store → Preferences (one manual click), policies/legal pages (#27), waitlist welcome email (#30)

## Phases & Milestones
### Phase 1: Foundation & Research
- [x] #1 Rules Compilation — `rules/gameplay-rules.md`
- [x] #2 Mood Board Research — `design/moodboard/` (37 images)
- [x] #4 Kanban Setup — [GitHub Project Board](https://github.com/users/ccwells/projects/2)
- [x] #7 Initial Rules Draft — `rules/gameplay-rules.md` v0.1
- [x] #16 Production equipment specs — `production/engraving/` + `production/printing/`
- [x] #11 Playing mat design — `design/mat/mat-design-final.png` (PR #20)
- [x] #6 Tile Design Concepts — 51 designs; `print-ready/` (32:23 crop) + `transparent/` (UV) exports; proof sheet PDF
- [x] #12 Tile rack design — spec + reference images (PR #35)
- [x] #3 Competitor Analysis — `research/competitor-analysis.md`
- [x] #5 User Personas — `research/user-personas.md`
- [x] #8 Business Model Canvas — `business/business-model-canvas.md`

### Phase 2: Design & Prototyping
- [x] #13 Dice design — spec + reference images (PR #35)
- [x] #14 Trinkets & accessories — spec + reference images (PR #35)
- [ ] #17 Adapt tile designs for UV printer — ✅ aspect ratio fixed (PR #34), ✅ transparent backgrounds (PR #36); remaining: CMYK test strips on tile material
- [ ] #18 Adapt tile designs for laser engraver — remaining: SVG engraving overlays, print-then-engrave workflow test
- [x] #21 Social media teaser images — 3 variants + hero banner/tile strip/og-image composites (`design/marketing/`)
- [ ] Tile blank material selection — sourcing spec done (`design/tile-blanks-spec.md`); **DECISION PENDING — blocks everything downstream**
- [ ] Tile mockups, playtesting simulations
- [ ] Digital prototype (medium TBD)

### Phase 3: Ecommerce Setup
- [x] #22 Shopify store setup & domain — live at maharajong.com
- [x] #23 Storefront: pre-order landing page live as homepage (`web/landing/`, Horizon theme + Custom Liquid section rendering `pages/maharajong`)
- [~] #24 Product catalog & listings — draft Founding Edition product created; publish when pricing is final
- [ ] #25 Payment processing & checkout optimization
- [ ] #26 Shipping, fulfillment & packaging
- [ ] #27 Legal compliance, policies & data protection
- [~] #28 SEO — homepage + landing page title/meta set; sitemap/keyword work remaining
- [ ] #29 Analytics, tracking & conversion measurement
- [~] #30 Email marketing — waitlist capture live (tag `preorder`); welcome/nurture flows not yet built
- [ ] #31 Pre-launch QA & testing — landing page verified desktop/mobile; checkout untested (no live product)
- [ ] #32 Launch marketing plan & go-live

## Repository Structure
- `README.md` — Vision + generation script usage
- `AGENTS.md` — Agent instructions (Grok for images)
- `rules/gameplay-rules.md` — Complete rules v0.1
- `/design/moodboard/` — 37 moodboard images (rangoli, temples, peacock, spice)
- `/design/tiles/` — 51 tile images + `print-ready/` + `transparent/`, generation/crop/export scripts, proof sheet
- `/design/mat/` — Mat design final + spec + `generate_mat.py`
- `/design/racks/`, `/design/dice/`, `/design/trinkets/` — Specs + reference images
- `/design/marketing/` — Teasers, hero composites (`hero/`), web-optimized exports (`web/`)
- `/design/tile-blanks-spec.md` — Tile blank sourcing: 3 suppliers, material comparison, next steps
- `/production/` — Equipment specs (xTool F2 Ultra, eufyMake E1) + tile production audit
- `/research/` — `competitor-analysis.md`, `user-personas.md`
- `/business/` — `business-model-canvas.md`
- `/web/landing/` — Landing page: `index.html` preview, `shopify-page.liquid` (deployed), `DEPLOY.md`
