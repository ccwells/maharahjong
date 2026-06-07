# eufyMake E1 — UV Printer Spec

## Product Info
- **Product**: eufyMake UV Printer E1
- **Model**: V8260
- **Product page**: https://www.eufymake.com/products/eufymake-e1
- **Support & user guide**: https://support.eufymake.com/s/product/a08J10000018M9hIAE/uv-printer-e1
- **Price**: From $2,499 USD (Basic Bundle) / $3,299 (Deluxe Bundle)
- **Purpose in Maharahjong**: Full-color UV printing of tile face artwork, mat printing (if neoprene sublimation is handled externally), and potentially printing on wood racks or other accessories

## Printing Specifications
- **Printer type**: Piezo inkjet UV flatbed printer
- **Print resolution**: 1,440 DPI
- **Color profile**: CMYKWG (Cyan, Magenta, Yellow, Black, White, Gloss — 6 channels)
- **Ink type**: UV-curable ink, instant LED curing
- **Ink cartridge size**: 100 ml per cartridge (proprietary eufyMake cartridges)
- **Embossed/3D texture height**: Up to 5 mm (via layered white ink or gloss)
- **Curing**: UV LED instant cure (no heat baking or air drying)

## Print Area
- **Standard flatbed**: 330 × 420 mm (13 × 16.5 inches, A3 size)
- **Mini flatbed**: 330 × 90 mm (13.2 × 3.54 inches)
- **Roll-to-film**: Up to 10 meters continuous
- **Supported print load**: 1.5 kg max per object on flatbed
- **Maximum object height** (camera recognition): 60 mm
- **Maximum printable object height**: 100 mm
- **Maximum height variation on single object**: 2 mm

## Camera & Positioning
- **Camera**: 8 MP built-in camera
- **Positioning**: Dual laser sensors + snapshot camera
- **Auto height adjustment range**: ±0.5 mm
- **Height measurement accuracy**: ±1 mm (through-beam laser sensor)
- **AI contour recognition**: Yes (limited on transparent substrates)
- **AutoFill**: AI-based multi-substrate batch positioning

## Supported Materials
Wood, metal, glass, ceramic, acrylic, plastic, leather, fabric (with flexible white ink), stone, rubber, silicone, canvas, paper, cardboard, and more (300+ materials)

**Notes on adhesion**:
- Glass / glazed ceramics: Pre-coating recommended to prevent peeling
- Metal: Pre-coating recommended in humid environments
- Acrylic: Pre-coating recommended for heavy-scratch resistance

## Software & Connectivity
- **Software**: eufyMake Studio (desktop) + eufyMake App (mobile)
- **Operating systems**: Windows / macOS / iOS / Android
- **Connection**: Wi-Fi IEEE 802.11 b/g/n 2.4 GHz, USB
- **Supported files**: JPEG, PNG, PDF
- **AI features**: Contour recognition, AutoFill batch positioning, design generation, background removal, 3D texture map creation

## Physical Specifications
- **Dimensions**: 590 × 250 × 407 mm (W × D × H)
- **Weight**: 20 kg (44 lb) / 23 kg (51 lb) with packaging
- **Max input power**: 66 W
- **Power adapter**: 100–240 V AC, 50–60 Hz

## Environmental Requirements
- **Operating temperature**: 15–35 °C (59–95 °F)
- **Operating humidity**: 20–85% RH
- **Operating noise**: <60 dB

## Safety & Certifications
- **UV light blocking**: >90% (under sealed enclosure conditions)
- **Air filtration**: Built-in activated carbon filter for odor/VOC reduction
- **Certifications**: Certified for low emissions, low blue light

## Included Accessories (Basic Bundle)
- eufyMake E1 UV Printer
- Standard flatbed (330 × 420 mm)
- Mini flatbed (330 × 90 mm, pre-installed)
- Standard adhesive mat
- Mini adhesive mat
- Air filter
- UV protective goggles
- Power adapter + power cable
- 2.5 mm hex key
- 3× free substrate samples
- Quick start guide

## Optional Accessories
- **Rotary printing attachment**: Print on cylinders/cones/mugs (40–100 mm diameter, taper ≤13°)
- **Roll-to-film attachment**: Continuous prints up to 10 meters
- **UV DTF laminating machine**: Print + laminate durable transfer stickers
- **Ink subscription plan**: Automatic discounted ink deliveries

## Ink System
- **Cartridges**: C (Cyan), M (Magenta), Y (Yellow), K (Black), W (White), G (Gloss)
- **Cleaning cartridge**: Infuses cleaning solution into nozzles post-print for automated maintenance
- **White ink**: Used most heavily — provides base layer for vivid color on dark/transparent substrates. 3 base layers default (adjustable to 0–1 if substrate is pre-painted white)
- **Gloss ink**: Optional top layer for high-gloss finish and scratch/weather resistance
- **Shelf life**: Check expiry; UV ink has limited shelf life

## Maintenance
- **JetClean™ system**: Automatic nozzle cleaning + moisturizing after each use
- **Routine cleaning** (monthly): Manual printhead cleaning per eufyMake instructions
- **Deep cleaning** (quarterly): More thorough manual cleaning procedure
- **Printhead replacement**: Consumable part — 3-month warranty
- **Air filter replacement**: Activated carbon filter, replace as needed
- **Ink pad & scraper kit**: Replace per usage guidelines

## Maharahjong Production Notes

### Tile face printing (primary use case)
- Tile face is 32 × 23 mm — the A3 flatbed (330 × 420 mm) can fit ~130 tiles per batch (10 × 13 grid with spacing)
- This means a full set of 152 tiles can be printed in ~2 flatbed runs
- Use the mini flatbed for small test batches or individual tile reprints
- White ink base layer is critical for vivid colors on ivory/cream tile material
- Gloss layer recommended for durability and the premium "lacquered" feel described in the tile spec
- 1,440 DPI provides more than enough detail for the tile designs at 32 × 23 mm
- The 3D texture capability (up to 5 mm) could add tactile embossing to tile faces — consider for honor tiles or special rangoli bonus tiles

### Color accuracy
- Calibrate color profiles to match the tile design spec palette:
  - Magenta-pink (Lotus suit)
  - Teal/blue-green (Peacock suit)
  - Royal purple (Vedic suit)
  - Saffron gold (Wind honors)
  - Jewel tones (Deity honors)
- Print test strips on actual tile material before production runs
- UV ink has a matte finish by default — apply gloss layer for the premium sheen

### Workflow integration with laser engraver
1. **Print first**: UV print the full-color tile artwork onto tile blanks using the eufyMake E1
2. **Engrave second**: Use the xTool F2 Ultra UV to add recessed line engravings, borders, or numeral details on top of the printed surface
3. **Test compatibility**: Verify that UV laser engraving on cured UV ink doesn't damage or discolor the print — run test samples first

### Design file preparation
- Export tile designs as high-DPI PNG (1,440 DPI or higher) with transparent backgrounds
- Use eufyMake Studio's camera positioning to align prints to tile blanks on the flatbed
- For batch runs: create a template layout with 130 tile positions at correct spacing
- Use AutoFill for multi-tile batch alignment once the template is calibrated

### Adhesion considerations
- Test UV ink adhesion on the specific tile material (resin? acrylic? melamine?)
- If adhesion is weak, apply pre-coating primer before printing
- Apply gloss overcoat for scratch resistance and longevity during gameplay
